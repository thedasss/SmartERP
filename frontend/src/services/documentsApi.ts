import { api } from './api';

export interface Document {
  id: string;
  filename: string;
  content_type: string;
  file_size: number;
  entity_type: string;
  entity_id?: string;
  created_at: string;
}

export const documentsApi = {
  getDocuments: async (entityType?: string, entityId?: string): Promise<Document[]> => {
    const params = new URLSearchParams();
    if (entityType) params.append('entity_type', entityType);
    if (entityId) params.append('entity_id', entityId);
    
    const { data } = await api.get(`/documents?${params.toString()}`);
    return data;
  },

  uploadDocument: async (file: File, entityType: string = 'GENERAL', entityId?: string): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('entity_type', entityType);
    if (entityId) formData.append('entity_id', entityId);

    const { data } = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  },

  deleteDocument: async (id: string): Promise<void> => {
    await api.delete(`/documents/${id}`);
  }
};
