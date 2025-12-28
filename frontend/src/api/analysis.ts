/**
 * Analysis API client for LLM-powered spending analysis.
 */

import apiClient from './index'

export interface AnalysisResponse {
  analysis: string
  period: string
  total_spending: number
  top_categories: Array<{
    name: string
    count: number
    amount: number
  }>
}

export async function getMonthlyAnalysis(
  year?: number,
  month?: number
): Promise<AnalysisResponse> {
  const response = await apiClient.post<AnalysisResponse>('/analysis/monthly', {
    year,
    month,
  })
  return response.data
}
