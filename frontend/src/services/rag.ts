import { authenticatedFetch, parseApiError } from './api'

export interface RAGSource {
  chunk_id: string
  document_id: string
  content: string
  score: number
}

export interface RAGResponse {
  answer: string
  sources: RAGSource[]
}

interface RAGAPIResponse {
  success: boolean
  message: string
  data: RAGResponse
}

export interface RAGQueryRequest {
  query: string
  top_k?: number
}

export async function queryRAG(
  payload: RAGQueryRequest,
): Promise<RAGResponse> {
  const response = await authenticatedFetch('/rag/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: payload.query,
      top_k: payload.top_k ?? 5,
    }),
  })

  if (!response.ok) {
    throw await parseApiError(
      response,
      'Unable to get an answer from the AI assistant.',
    )
  }

  const result = (await response.json()) as RAGAPIResponse

  if (!result.success || !result.data) {
    throw new Error(
      result.message || 'The AI assistant could not generate an answer.',
    )
  }

  return result.data
}