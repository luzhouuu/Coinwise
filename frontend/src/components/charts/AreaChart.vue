<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { EChartsOption } from 'echarts'

use([LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent, CanvasRenderer])

interface Dataset {
  label: string
  data: number[]
  color?: string
}

interface Props {
  labels: string[]
  datasets: Dataset[]
  showLegend?: boolean
  smooth?: boolean
  fillOpacity?: number
  scrollable?: boolean
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showLegend: true,
  smooth: true,
  fillOpacity: 0.15,
  scrollable: false,
  clickable: false,
})

const emit = defineEmits<{
  click: [index: number, label: string]
}>()

// Chart reference for global click handling
const chartRef = ref<InstanceType<typeof VChart> | null>(null)

// Setup global click handler on chart area
function setupClickHandler() {
  if (!props.clickable || !chartRef.value) return

  const chart = chartRef.value.chart
  if (!chart) return

  chart.getZr().on('click', (params: any) => {
    const pointInPixel = [params.offsetX, params.offsetY]
    if (chart.containPixel('grid', pointInPixel)) {
      const pointInGrid = chart.convertFromPixel({ seriesIndex: 0 }, pointInPixel)
      if (pointInGrid && pointInGrid[0] !== undefined) {
        const xIndex = Math.round(pointInGrid[0])
        if (xIndex >= 0 && xIndex < props.labels.length) {
          emit('click', xIndex, props.labels[xIndex] || '')
        }
      }
    }
  })
}

onMounted(() => {
  // Wait for chart to be ready
  setTimeout(setupClickHandler, 100)
})

// Re-setup when clickable changes
watch(() => props.clickable, (newVal) => {
  if (newVal) {
    setTimeout(setupClickHandler, 100)
  }
})

const defaultColors = [
  '#007AFF', '#34C759', '#FF9500', '#FF3B30', '#5AC8FA',
  '#AF52DE', '#FF2D55', '#A2845E', '#8E8E93', '#64D2FF',
]

const hexToRgba = (hex: string, alpha: number): string => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

const chartOption = computed((): EChartsOption => {
  const series = props.datasets.map((ds, index) => {
    const color = ds.color || defaultColors[index % defaultColors.length] || '#007AFF'
    return {
      name: ds.label,
      type: 'line' as const,
      data: ds.data,
      smooth: props.smooth,
      symbol: 'circle',
      symbolSize: props.clickable ? 8 : 0,
      showSymbol: false,
      cursor: props.clickable ? 'pointer' : 'default',
      triggerLineEvent: props.clickable,
      lineStyle: {
        width: 2,
        color: color,
      },
      itemStyle: {
        color: color,
      },
      areaStyle: {
        color: {
          type: 'linear' as const,
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: hexToRgba(color, props.fillOpacity * 2) },
            { offset: 1, color: hexToRgba(color, 0) },
          ],
        },
      },
      emphasis: {
        focus: 'series' as const,
        itemStyle: {
          color: color,
          borderColor: '#fff',
          borderWidth: 2,
          shadowBlur: 4,
          shadowColor: 'rgba(0,0,0,0.2)',
        },
      },
    }
  })

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#FFFFFF',
      borderColor: '#E5E5EA',
      borderWidth: 1,
      borderRadius: 12,
      padding: 12,
      textStyle: {
        color: '#1D1D1F',
        fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif",
      },
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#999',
        },
        lineStyle: {
          color: '#007AFF',
          width: 1,
          type: 'dashed',
        },
      },
      formatter: (params: any) => {
        if (!Array.isArray(params)) return ''
        const clickHint = props.clickable ? '<div style="font-size:11px;color:#86868B;margin-top:8px;">点击查看详情</div>' : ''
        let result = `<div style="font-weight:600;margin-bottom:8px;">${params[0].axisValue}</div>`
        params.forEach((item: any) => {
          result += `<div style="display:flex;align-items:center;gap:8px;margin-top:4px;">
            <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${item.color};"></span>
            <span style="color:#86868B;">${item.seriesName}:</span>
            <span style="font-weight:500;">¥${item.value.toLocaleString()}</span>
          </div>`
        })
        return result + clickHint
      },
    },
    legend: {
      show: props.showLegend && props.datasets.length > 1,
      top: 0,
      right: 0,
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 16,
      icon: 'circle',
      textStyle: {
        color: '#1D1D1F',
        fontSize: 13,
        fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif",
      },
    },
    grid: {
      left: 10,
      right: 10,
      top: props.showLegend && props.datasets.length > 1 ? 40 : 10,
      bottom: props.scrollable ? 24 : 10,
      containLabel: true,
    },
    dataZoom: props.scrollable ? [
      {
        type: 'slider',
        show: true,
        xAxisIndex: 0,
        start: 0,
        end: 100,
        height: 4,
        bottom: 8,
        borderColor: 'transparent',
        backgroundColor: 'rgba(0,0,0,0.06)',
        fillerColor: '#007AFF',
        borderRadius: 2,
        handleIcon: 'circle',
        handleSize: 12,
        handleStyle: {
          color: '#007AFF',
          borderColor: '#fff',
          borderWidth: 2,
          shadowBlur: 4,
          shadowColor: 'rgba(0,0,0,0.15)',
        },
        moveHandleSize: 0,
        showDetail: false,
        showDataShadow: false,
        brushSelect: false,
      },
      {
        type: 'inside',
        xAxisIndex: 0,
        start: 0,
        end: 100,
        zoomOnMouseWheel: 'shift',
        moveOnMouseWheel: true,
      }
    ] : undefined,
    xAxis: {
      type: 'category',
      data: props.labels,
      boundaryGap: false,
      triggerEvent: props.clickable,
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: {
        color: '#86868B',
        fontSize: 12,
        fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif",
      },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: {
        lineStyle: { color: 'rgba(0, 0, 0, 0.05)' },
      },
      axisLabel: {
        color: '#86868B',
        fontSize: 12,
        fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif",
        formatter: (value: number) => `¥${value.toLocaleString()}`,
      },
    },
    series,
  }
})
</script>

<template>
  <div class="area-chart">
    <VChart
      ref="chartRef"
      :option="chartOption"
      autoresize
    />
  </div>
</template>

<style scoped>
.area-chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
}
</style>
