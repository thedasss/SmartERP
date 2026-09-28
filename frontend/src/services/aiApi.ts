import { api } from './api';

export const aiApi = {
  chat: async (message: string): Promise<string> => {
    const { data } = await api.post('/ai/chat', { message });
    return data.reply;
  },
  indexData: async (): Promise<string> => {
    const { data } = await api.post('/ai/index');
    return data.message;
  }
};
