<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { EChartsOption } from 'echarts'

use([PieChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer])

interface Props {
  labels: string[]
  data: number[]
  colors?: string[]
  donut?: boolean
  showLegend?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  colors: () => [
    '#007AFF', '#34C759', '#FF9500', '#FF3B30', '#5AC8FA',
    '#AF52DE', '#FF2D55', '#A2845E', '#8E8E93', '#64D2FF',
  ],
  donut: false,
  showLegend: true,
})

const chartOption = computed((): EChartsOption => {
  const seriesData = props.labels.map((label, index) => ({
    name: label,
    value: props.data[index] ?? 0,
    itemStyle: {
      color: props.colors[index % props.colors.length],
    },
  }))

  return {
    tooltip: {
      trigger: 'item',
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
        const value = params.value
        const percent = params.percent
        return `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${params.color};margin-right:8px;"></span>${params.name}<br/>¥${value.toLocaleString()} (${percent}%)`
      },
    },
    legend: {
      show: props.showLegend,
      orient: 'vertical',
      right: 10,
      top: 'center',
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
    series: [
      {
        type: 'pie',
        radius: props.donut ? ['45%', '70%'] : '70%',
        center: props.showLegend ? ['35%', '50%'] : ['50%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: props.donut ? 4 : 0,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: false,
        },
        emphasis: {
          scale: true,
          scaleSize: 8,
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.2)',
          },
        },
        data: seriesData,
      },
    ],
  }
})
</script>

<template>
  <div class="pie-chart">
    <VChart :option="chartOption" autoresize />
  </div>
</template>

<style scoped>
.pie-chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
}
</style>
