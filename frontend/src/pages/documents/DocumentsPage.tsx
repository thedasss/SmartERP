import React, { useState, useEffect, useRef } from 'react';
import type { Document } from '../../services/documentsApi';
import { documentsApi } from '../../services/documentsApi';

export const DocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const data = await documentsApi.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error('Failed to fetch documents', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await documentsApi.uploadDocument(file);
      await fetchDocuments();
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      console.error('Failed to upload file', err);
      alert('Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    try {
      await documentsApi.deleteDocument(id);
      await fetchDocuments();
    } catch (err) {
      console.error('Failed to delete document', err);
      alert('Failed to delete document');
    }
  };

  const getFileIcon = (contentType: string) => {
    if (contentType.includes('pdf')) return '📕';
    if (contentType.includes('image')) return '🖼️';
    if (contentType.includes('sheet') || contentType.includes('excel')) return '📊';
    return '📄';
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-500 mt-1">Manage all your files and attachments</p>
        </div>
        <div>
            <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                onChange={handleFileChange} 
            />
            <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm font-medium disabled:opacity-50"
            >
                {uploading ? 'Uploading...' : 'Upload File'}
            </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      ) : documents.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
          <div className="text-gray-400 mb-4 text-5xl">🗂️</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Documents Yet</h3>
          <p className="text-gray-500 max-w-md mx-auto mb-6">
            Upload files like contracts, invoices, and receipts to keep them organized.
          </p>
          <button
              onClick={() => fileInputRef.current?.click()}
              className="text-indigo-600 font-medium hover:text-indigo-800"
          >
              Click here to upload your first file
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100">
                  <th className="p-4 text-sm font-semibold text-gray-600">Name</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Linked To</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Size</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Uploaded</th>
                  <th className="p-4 text-sm font-semibold text-gray-600 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50 transition-colors">
                    <td className="p-4 text-sm font-medium text-gray-900 flex items-center gap-3">
                        <span className="text-xl">{getFileIcon(doc.content_type)}</span>
                        {doc.filename}
                    </td>
                    <td className="p-4 text-sm text-gray-600">
                        {doc.entity_type === 'GENERAL' ? (
                            <span className="text-gray-400 italic">General</span>
                        ) : (
                            <span className="bg-gray-100 px-2 py-1 rounded text-xs font-medium">{doc.entity_type}</span>
                        )}
                    </td>
                    <td className="p-4 text-sm text-gray-600">{formatSize(doc.file_size)}</td>
                    <td className="p-4 text-sm text-gray-600">{new Date(doc.created_at).toLocaleDateString()}</td>
                    <td className="p-4 text-sm text-right space-x-3">
                        <a 
                            href={`http://localhost:8000/api/v1/documents/${doc.id}/download`} 
                            target="_blank" 
                            rel="noreferrer"
                            className="text-indigo-600 hover:text-indigo-800 font-medium"
                        >
                            Download
                        </a>
                        <button
                            onClick={() => handleDelete(doc.id)}
                            className="text-red-600 hover:text-red-800 font-medium"
                        >
                            Delete
                        </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
