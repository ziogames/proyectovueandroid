<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
} from 'chart.js';
import { Bar, Doughnut } from 'vue-chartjs';
import llaveService, { type Llave } from '../services/llaveService';
import proveedorService, { type Proveedor } from '../services/proveedorService';
import historyService, { type CheckoutHistoryItem } from '../services/historyService';
import { Line } from 'vue-chartjs';

// Definir props
const props = defineProps<{
    currentUserId?: number | null;
}>();

// Registro de componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Filler,
  Title,
  Tooltip,
  Legend
);

const llaves = ref<Llave[]>([]);
const proveedores = ref<Proveedor[]>([]);
const history = ref<CheckoutHistoryItem[]>([]);

const loadData = async () => {
    try {
        const [llavesRes, provRes, histRes] = await Promise.all([
            llaveService.getLlaves(),
            proveedorService.getProveedores(),
            historyService.getHistory()
        ]);
        llaves.value = llavesRes.data;
        proveedores.value = provRes.data;
        history.value = histRes.data;
    } catch (error) {
        console.error("Error cargando datos para gráficos", error);
    }
};

// Datos para Gráfico de Barras: Stock por Código de Llave
const barChartData = computed(() => {
    return {
        labels: llaves.value.map(l => l.cod_llave),
        datasets: [{
            label: 'Inventario Disponible',
            backgroundColor: 'rgba(79, 70, 229, 0.8)',
            hoverBackgroundColor: 'rgba(129, 140, 248, 0.9)',
            borderColor: 'rgba(129, 140, 248, 1)',
            borderWidth: 2,
            borderRadius: 8,
            borderSkipped: false,
            data: llaves.value.map(l => l.cantidad)
        }]
    };
});

const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
        duration: 1200,
        easing: 'easeInOutQuart' as const
    },
    plugins: {
        legend: {
             labels: { 
                 color: 'white',
                 font: { weight: 'bold' as const, size: 12 },
                 padding: 15
             }
        },
        title: {
             display: true,
             text: 'Cantidad de Llaves Disponibles por Código',
             color: 'white',
             font: { size: 14, weight: 'bold' as const },
             padding: 15
        },
        tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(129, 140, 248, 0.5)',
            borderWidth: 1,
            padding: 12,
            titleFont: { weight: 'bold' as const },
            displayColors: false
        }
    },
    scales: {
        y: {
            ticks: {
                 color: '#cbd5e1',
                 font: { weight: 'bold' as const, size: 10 }
            },
            grid: {
                 color: 'rgba(255, 255, 255, 0.08)',
                 drawBorder: false
            },
            beginAtZero: true
        },
        x: {
            ticks: {
                 color: '#cbd5e1',
                 font: { weight: 'bold' as const, size: 10 }
            },
            grid: {
                 display: false
            }
        }
    }
};

// Datos para Gráfico de Dona: Distribución por Proveedor
const doughnutChartData = computed(() => {
    // Calcular conteo de llaves por proveedor
    // Primero, crear un mapa de proveedor ID a nombre
    const provMap = new Map<number, string>();
    proveedores.value.forEach(p => {
        if (p.id) provMap.set(p.id, p.nombre);
    });

    const counts = new Map<string, number>();
    
    // Inicializar contadores
    proveedores.value.forEach(p => counts.set(p.nombre, 0));

    // Contar
    llaves.value.forEach(l => {
        const pName = provMap.get(l.proveedor) || 'Desconocido';
        const current = counts.get(pName) || 0;
        counts.set(pName, current + 1); // Contamos tipos de llaves por proveedor, no cantidad total
    });

    const colors = [
        'rgba(59, 130, 246, 0.8)',   // Blue
        'rgba(16, 185, 129, 0.8)',   // Emerald
        'rgba(245, 158, 11, 0.8)',   // Amber
        'rgba(239, 68, 68, 0.8)',    // Red
        'rgba(139, 92, 246, 0.8)',   // Violet
        'rgba(236, 72, 153, 0.8)',   // Pink
        'rgba(34, 197, 94, 0.8)'     // Green
    ];

    return {
        labels: Array.from(counts.keys()),
        datasets: [{
            backgroundColor: colors.slice(0, Array.from(counts.keys()).length),
            borderColor: 'rgba(30, 41, 59, 1)',
            borderWidth: 2,
            data: Array.from(counts.values()),
            hoverBorderColor: 'white',
            hoverBorderWidth: 3
        }]
    };
});

const doughnutChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
        animateRotate: true,
        animateScale: false,
        duration: 1000
    },
    plugins: {
        legend: {
             labels: { 
                 color: '#cbd5e1', 
                 font: { weight: 'bold' as const, size: 11 },
                 padding: 20,
                 usePointStyle: true,
                 pointStyle: 'circle'
             },
             position: 'right' as const
        },
        title: { display: false },
        tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(129, 140, 248, 0.5)',
            borderWidth: 1,
            padding: 12,
            titleFont: { weight: 'bold' as const },
            callbacks: {
                label: (context: any) => {
                    const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
                    const percentage = ((context.parsed / total) * 100).toFixed(1);
                    return `${context.label}: ${context.parsed} (${percentage}%)`;
                }
            }
        }
    }
};

// Datos para Gráfico de Linea: Salidas por Fecha (Filtradas por usuario actual)
const lineChartData = computed(() => {
    const counts = new Map<string, number>();
    
    // Filtrar historia solo del usuario actual si se proporciona
    let filteredHistory = history.value;
    if (props.currentUserId) {
        filteredHistory = history.value.filter(item => item.user === props.currentUserId);
    }
    
    // Ordenar por fecha ascendente
    const sortedHistory = [...filteredHistory].sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime());

    sortedHistory.forEach(item => {
        const date = new Date(item.fecha).toLocaleDateString();
        const current = counts.get(date) || 0;
        counts.set(date, current + item.cantidad);
    });

    return {
        labels: Array.from(counts.keys()),
        datasets: [{
            label: 'Llaves Retiradas',
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            borderColor: 'rgba(16, 185, 129, 1)',
            borderWidth: 3,
            fill: true,
            data: Array.from(counts.values()),
            tension: 0.4,
            pointRadius: 5,
            pointHoverRadius: 7,
            pointBackgroundColor: 'rgba(16, 185, 129, 1)',
            pointBorderColor: 'white',
            pointBorderWidth: 2,
            hoverBackgroundColor: 'rgba(16, 185, 129, 0.8)'
        }]
    };
});

const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
        duration: 1200,
        easing: 'easeInOutQuart' as const
    },
    plugins: {
        legend: { 
            display: true,
            labels: {
                color: '#cbd5e1',
                font: { weight: 'bold' as const, size: 12 },
                padding: 15
            }
        },
        title: { display: false },
        tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(16, 185, 129, 0.5)',
            borderWidth: 1,
            padding: 12,
            titleFont: { weight: 'bold' as const },
            displayColors: false
        }
    },
    scales: {
        y: { 
            beginAtZero: true,
            ticks: { 
                color: '#cbd5e1', 
                font: { weight: 'bold' as const, size: 10 },
                padding: 8
            }, 
            grid: { 
                color: 'rgba(255, 255, 255, 0.08)', 
                drawBorder: false 
            } 
        },
        x: { 
            ticks: { 
                color: '#cbd5e1', 
                font: { weight: 'bold' as const, size: 10 },
                maxRotation: 45,
                minRotation: 0
            }, 
            grid: { display: false } 
        }
    }
};

// Datos para Gráfico de Barras Horizontal: Salidas por Usuario
const userChartData = computed(() => {
    const counts = new Map<string, number>();
    
    history.value.forEach(item => {
        const user = item.user_name || 'Desconocido';
        const current = counts.get(user) || 0;
        counts.set(user, current + item.cantidad);
    });

    return {
        labels: Array.from(counts.keys()),
        datasets: [{
            label: 'Total Llaves Retiradas',
            backgroundColor: [
                'rgba(251, 146, 60, 0.8)',    // Orange
                'rgba(245, 158, 11, 0.8)',    // Amber
                'rgba(217, 119, 6, 0.8)',     // Yellow
                'rgba(236, 72, 153, 0.8)',    // Pink
                'rgba(168, 85, 247, 0.8)'     // Purple
            ],
            hoverBackgroundColor: [
                'rgba(251, 146, 60, 1)',
                'rgba(245, 158, 11, 1)',
                'rgba(217, 119, 6, 1)',
                'rgba(236, 72, 153, 1)',
                'rgba(168, 85, 247, 1)'
            ],
            borderColor: 'rgba(255, 255, 255, 0.2)',
            borderWidth: 2,
            borderRadius: 8,
            data: Array.from(counts.values())
        }]
    };
});

const userChartOptions = {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    animation: {
        duration: 1200,
        easing: 'easeInOutQuart' as const
    },
    plugins: {
        legend: { 
            display: true,
            labels: {
                color: '#cbd5e1',
                font: { weight: 'bold' as const, size: 12 },
                padding: 15
            }
        },
        title: { display: false },
        tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(251, 146, 60, 0.5)',
            borderWidth: 1,
            padding: 12,
            titleFont: { weight: 'bold' as const },
            displayColors: false
        }
    },
    scales: {
        y: { 
            ticks: { 
                color: '#cbd5e1', 
                font: { weight: 'bold' as const, size: 10 },
                padding: 8
            }, 
            grid: { display: false } 
        },
        x: { 
            beginAtZero: true,
            ticks: { 
                color: '#cbd5e1', 
                font: { weight: 'bold' as const, size: 10 },
                padding: 8
            }, 
            grid: { 
                color: 'rgba(255, 255, 255, 0.08)', 
                drawBorder: false 
            } 
        }
    }
};

onMounted(() => {
    loadData();
});
</script>

<template>
  <div class="space-y-8">
    <!-- Fila 1: Gráficos principales -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Gráfico de Barras: Stock por Código -->
        <div class="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl border border-slate-700/50 p-6 h-96 hover:border-slate-600/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-indigo-600/5 to-transparent rounded-2xl pointer-events-none"></div>
            <Bar :data="barChartData" :options="barChartOptions" />
        </div>

        <!-- Gráfico de Dona: Distribución por Proveedor -->
        <div class="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl border border-slate-700/50 p-6 h-96 flex items-center justify-center hover:border-slate-600/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-blue-600/5 to-transparent rounded-2xl pointer-events-none"></div>
            <Doughnut :data="doughnutChartData" :options="doughnutChartOptions" />
        </div>
    </div>

    <!-- Fila 2: Timeline y Usuarios -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Gráfico de Linea: Timeline de Salidas -->
        <div class="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl border border-slate-700/50 p-6 h-96 hover:border-slate-600/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-emerald-600/5 to-transparent rounded-2xl pointer-events-none"></div>
            <Line :data="lineChartData" :options="lineChartOptions" />
        </div>

        <!-- Gráfico de Barras Horizontal: Salidas por Usuario -->
        <div class="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl border border-slate-700/50 p-6 h-96 hover:border-slate-600/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-orange-600/5 to-transparent rounded-2xl pointer-events-none"></div>
            <Bar :data="userChartData" :options="userChartOptions" />
        </div>
    </div>

    <!-- Fila 3: KPIs Rápidos Mejorados -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <!-- Total Tipos de Llave -->
        <div class="relative overflow-hidden rounded-2xl border border-indigo-700/30 p-6 group">
            <div class="absolute inset-0 bg-gradient-to-br from-indigo-600/20 via-indigo-600/5 to-transparent group-hover:from-indigo-600/30 group-hover:via-indigo-600/10 transition-all duration-300"></div>
            <div class="absolute inset-0 rounded-2xl border border-indigo-400/0 group-hover:border-indigo-400/20 transition-all duration-300"></div>
            <div class="relative z-10">
                <div class="flex items-center justify-between mb-3">
                    <h4 class="text-slate-400 text-xs uppercase font-bold tracking-widest">Total Tipos de Llave</h4>
                    <div class="w-10 h-10 rounded-lg bg-indigo-600/20 flex items-center justify-center">
                        <svg class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                        </svg>
                    </div>
                </div>
                <p class="text-4xl font-black text-indigo-300">{{ llaves.length }}</p>
                <p class="text-xs text-slate-500 mt-2">modelos únicos en inventario</p>
            </div>
        </div>

        <!-- Stock Total Actual -->
        <div class="relative overflow-hidden rounded-2xl border border-emerald-700/30 p-6 group">
            <div class="absolute inset-0 bg-gradient-to-br from-emerald-600/20 via-emerald-600/5 to-transparent group-hover:from-emerald-600/30 group-hover:via-emerald-600/10 transition-all duration-300"></div>
            <div class="absolute inset-0 rounded-2xl border border-emerald-400/0 group-hover:border-emerald-400/20 transition-all duration-300"></div>
            <div class="relative z-10">
                <div class="flex items-center justify-between mb-3">
                    <h4 class="text-slate-400 text-xs uppercase font-bold tracking-widest">Stock Total Actual</h4>
                    <div class="w-10 h-10 rounded-lg bg-emerald-600/20 flex items-center justify-center">
                        <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                    </div>
                </div>
                <p class="text-4xl font-black text-emerald-300">{{ llaves.reduce((acc, curr) => acc + curr.cantidad, 0) }}</p>
                <p class="text-xs text-slate-500 mt-2">unidades disponibles</p>
            </div>
        </div>

        <!-- Total Proveedores -->
        <div class="relative overflow-hidden rounded-2xl border border-purple-700/30 p-6 group">
            <div class="absolute inset-0 bg-gradient-to-br from-purple-600/20 via-purple-600/5 to-transparent group-hover:from-purple-600/30 group-hover:via-purple-600/10 transition-all duration-300"></div>
            <div class="absolute inset-0 rounded-2xl border border-purple-400/0 group-hover:border-purple-400/20 transition-all duration-300"></div>
            <div class="relative z-10">
                <div class="flex items-center justify-between mb-3">
                    <h4 class="text-slate-400 text-xs uppercase font-bold tracking-widest">Total Proveedores</h4>
                    <div class="w-10 h-10 rounded-lg bg-purple-600/20 flex items-center justify-center">
                        <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                    </div>
                </div>
                <p class="text-4xl font-black text-purple-300">{{ proveedores.length }}</p>
                <p class="text-xs text-slate-500 mt-2">asociados activos</p>
            </div>
        </div>
    </div>
  </div>
</template>
