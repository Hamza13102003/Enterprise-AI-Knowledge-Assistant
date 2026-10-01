import { authenticatedFetch, parseApiError } from './api'

export interface DocumentItem {
  id: string
  filename: string
  content_type: string
  file_size: number
  status: string
  chunks_count: number
  uploaded_by: string | null
  created_at: string
  updated_at: string
}

export interface DocumentListResponse {
  documents: DocumentItem[]
}

export interface DocumentUploadResponse {
  document_id: string
  filename: string
  chunks_indexed: number
  message: string
}

export async function getDocuments(): Promise<DocumentItem[]> {
  const response = await authenticatedFetch('/documents')

  if (!response.ok) {
    throw await parseApiError(
      response,
      'Unable to load your documents.',
    )
  }

  const data = (await response.json()) as DocumentListResponse
  return data.documents
}

export async function uploadDocument(
  file: File,
): Promise<DocumentUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await authenticatedFetch('/documents/upload', {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw await parseApiError(
      response,
      'Unable to upload the document.',
    )
  }

  return response.json() as Promise<DocumentUploadResponse>
}

export async function deleteDocument(documentId: string): Promise<void> {
  const response = await authenticatedFetch(
    `/documents/${documentId}`,
    {
      method: 'DELETE',
    },
  )

  if (!response.ok) {
    throw await parseApiError(
      response,
      'Unable to delete the document.',
    )
  }
}
