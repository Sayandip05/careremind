import { useState, useRef } from 'react';
import { uploadApi } from '@/api/upload';
import { Upload as UploadIcon, Camera, CheckCircle } from 'lucide-react';

export default function Upload() {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [uploadType, setUploadType] = useState<'excel' | 'photo'>('excel');
  const [dragActive, setDragActive] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setError('');
    setResult(null);
    setUploading(true);
    try {
      const res = uploadType === 'excel'
        ? await uploadApi.uploadExcel(file)
        : await uploadApi.uploadPhoto(file);
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-800">Upload</h1>
        <p className="text-sm text-slate-500 mt-0.5">Upload Excel sheets or photos of your patient register</p>
      </div>

      {/* Type Toggle */}
      <div className="flex gap-2">
        {(['excel', 'photo'] as const).map((type) => (
          <button
            key={type}
            onClick={() => setUploadType(type)}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              uploadType === type
                ? 'bg-slate-900 text-white'
                : 'border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {type === 'excel' ? <UploadIcon className="w-4 h-4" /> : <Camera className="w-4 h-4" />}
            {type === 'excel' ? 'Excel' : 'Photo'}
          </button>
        ))}
      </div>

      {/* Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={(e) => { e.preventDefault(); setDragActive(false); if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]); }}
        onClick={() => fileRef.current?.click()}
        className={`cursor-pointer border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
          dragActive ? 'border-slate-400 bg-slate-50' : 'border-slate-200 hover:border-slate-300'
        }`}
      >
        <input ref={fileRef} type="file" accept={uploadType === 'excel' ? '.xlsx,.xls' : 'image/*'} onChange={(e) => { if (e.target.files?.[0]) handleFile(e.target.files[0]); }} className="hidden" />
        {uploading ? (
          <div>
            <div className="w-6 h-6 border-2 border-slate-200 border-t-slate-600 rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-slate-600">Processing...</p>
          </div>
        ) : (
          <div>
            {uploadType === 'excel' ? <UploadIcon className="w-8 h-8 text-slate-300 mx-auto mb-3" /> : <Camera className="w-8 h-8 text-slate-300 mx-auto mb-3" />}
            <p className="text-sm text-slate-600">Drop your {uploadType === 'excel' ? '.xlsx file' : 'photo'} here, or <span className="text-slate-900 font-medium">browse</span></p>
            <p className="text-xs text-slate-400 mt-1">{uploadType === 'excel' ? 'Max 10 MB' : 'Max 20 MB'}</p>
          </div>
        )}
      </div>

      {error && <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">{error}</p>}

      {result && (
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span className="text-sm font-medium text-slate-700">Upload successful</span>
          </div>
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Total Rows', value: result.total_rows },
              { label: 'New Patients', value: result.new_patients },
              { label: 'Duplicates', value: result.duplicates },
              { label: 'Skipped', value: result.skipped },
            ].map((item) => (
              <div key={item.label} className="text-center">
                <p className="text-xl font-semibold text-slate-800">{item.value}</p>
                <p className="text-xs text-slate-500">{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
