<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { EChartsOption } from 'echarts'

use([LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

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
}

const props = withDefaults(defineProps<Props>(), {
  showLegend: true,
  smooth: true,
})

const defaultColors = [
  '#007AFF', '#34C759', '#FF9500', '#FF3B30', '#5AC8FA',
  '#AF52DE', '#FF2D55', '#A2845E', '#8E8E93', '#64D2FF',
]

const chartOption = computed((): EChartsOption => {
  const series = props.datasets.map((ds, index) => ({
    name: ds.label,
    type: 'line' as const,
    data: ds.data,
    smooth: props.smooth,
    symbol: 'circle',
    symbolSize: 8,
    lineStyle: {
      width: 2,
      color: ds.color || defaultColors[index % defaultColors.length],
    },
    itemStyle: {
      color: '#FFFFFF',
      borderColor: ds.color || defaultColors[index % defaultColors.length],
      borderWidth: 2,
    },
    emphasis: {
      scale: true,
      itemStyle: {
        shadowBlur: 10,
        shadowColor: 'rgba(0, 0, 0, 0.2)',
      },
    },
  }))

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
      formatter: (params: any) => {
        if (!Array.isArray(params)) return ''
        let result = `<div style="font-weight:600;margin-bottom:8px;">${params[0].axisValue}</div>`
        params.forEach((item: any) => {
          result += `<div style="display:flex;align-items:center;gap:8px;margin-top:4px;">
            <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${item.color};"></span>
            <span style="color:#86868B;">${item.seriesName}:</span>
            <span style="font-weight:500;">¥${item.value.toLocaleString()}</span>
          </div>`
        })
        return result
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
      bottom: 10,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: props.labels,
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
  <div class="line-chart">
    <VChart :option="chartOption" autoresize />
  </div>
</template>

<style scoped>
.line-chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
}
</style>
