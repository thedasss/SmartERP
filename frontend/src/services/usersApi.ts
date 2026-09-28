import { api } from './api';
import type { PaginatedResponse } from '@/types';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface CreateUserPayload {
  email: string;
  password?: string;
  first_name: string;
  last_name: string;
  role: string;
}

export interface UpdateUserPayload {
  first_name?: string;
  last_name?: string;
  role?: string;
  is_active?: boolean;
}

export const usersApi = {
  getUsers: async (page = 1, pageSize = 20): Promise<PaginatedResponse<User>> => {
    const { data } = await api.get('/users', {
      params: { page, page_size: pageSize }
    });
    return data;
  },

  createUser: async (payload: CreateUserPayload): Promise<User> => {
    const { data } = await api.post('/users', payload);
    return data.data;
  },

  updateUser: async (id: string, payload: UpdateUserPayload): Promise<User> => {
    const { data } = await api.patch(`/users/${id}`, payload);
    return data.data;
  },

  deactivateUser: async (id: string): Promise<void> => {
    await api.delete(`/users/${id}`);
  }
};
