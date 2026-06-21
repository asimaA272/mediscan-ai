import React, { useState } from 'react'
import { UploadCloud, Loader2, AlertCircle, FileText } from 'lucide-react'
import { uploadScan } from '../services/api'

export default function XRayAnalysis() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    const selected = e.target.files[0]
    if (!selected) return
    setFile(selected)
    setResult(null)
    setError(null)
    if (selected.type.startsWith('image/')) {
      setPreview(URL.createObjectURL(selected))
    } else {
      setPreview(null) // DICOM files won't preview directly in <img>
    }
  }

  const handleAnalyze = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const res = await uploadScan(file)
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Scan failed. Check that the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-6xl">
      <header className="mb-6">
        <h1 className="font-display text-2xl font-semibold tracking-tight">X-Ray Analysis</h1>
        <p className="text-muted text-sm mt-1">
          Upload a chest X-ray to run the full 5-agent diagnostic pipeline.
        </p>
      </header>

      <div className="grid grid-cols-2 gap-6">
        {/* Upload zone */}
        <div className="bg-bg-panel border border-line rounded-xl p-6">
          <label
            htmlFor="scan-upload"
            className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-line rounded-lg cursor-pointer hover:border-accent-cyan/50 transition-colors"
          >
            {preview ? (
              <img src={preview} alt="Scan preview" className="h-full object-contain rounded" />
            ) : (
              <>
                <UploadCloud size={32} className="text-muted mb-3" />
                <p className="text-sm text-muted">
                  {file ? file.name : 'Click to upload .dcm, .png, or .jpg'}
                </p>
              </>
            )}
          </label>
          <input
            id="scan-upload"
            type="file"
            accept=".dcm,.png,.jpg,.jpeg"
            className="hidden"
            onChange={handleFileChange}
          />

          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="w-full mt-4 py-2.5 rounded-lg bg-accent-cyan text-bg font-medium text-sm disabled:opacity-40 disabled:cursor-not-allowed hover:bg-accent-cyan/90 transition-colors flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Running pipeline...
              </>
            ) : (
              'Run diagnostic pipeline'
            )}
          </button>

          {error && (
            <div className="mt-3 flex items-start gap-2 text-sm text-accent-red bg-accent-red/10 rounded-lg p-3">
              <AlertCircle size={16} className="shrink-0 mt-0.5" />
              {error}
            </div>
          )}
        </div>

        {/* Results */}
        <div className="bg-bg-panel border border-line rounded-xl p-6 min-h-[20rem]">
          <h3 className="font-display font-semibold mb-4">Findings</h3>
          {!result && (
            <p className="text-sm text-muted">Upload and analyze a scan to see results here.</p>
          )}
          {result && (
            <div className="space-y-4">
              {result.findings.map((f, i) => (
                <div key={i}>
                  <div className="flex justify-between text-sm mb-1">
                    <span>{f.label}</span>
                    <span className="text-muted">{Math.round(f.confidence * 100)}%</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-bg-elevated overflow-hidden">
                    <div
                      className="h-full bg-accent-cyan rounded-full"
                      style={{ width: `${Math.round(f.confidence * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Differentials + Report */}
      {result && (
        <div className="grid grid-cols-2 gap-6 mt-6">
          <div className="bg-bg-panel border border-line rounded-xl p-6">
            <h3 className="font-display font-semibold mb-4">Differential diagnoses</h3>
            <div className="space-y-3">
              {result.differentials.map((d, i) => (
                <div key={i} className="flex items-start justify-between gap-3 py-2 border-b border-line last:border-0">
                  <div>
                    <div className="text-sm font-medium">{d.diagnosis}</div>
                    <div className="text-xs text-muted mt-0.5">{d.reasoning}</div>
                  </div>
                  <span className="text-xs text-accent-cyan shrink-0">{Math.round(d.probability * 100)}%</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-bg-panel border border-line rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <FileText size={18} className="text-accent-green" />
              <h3 className="font-display font-semibold">Drafted report</h3>
            </div>
            <pre className="text-sm text-[#C9D2E0] whitespace-pre-wrap font-body leading-relaxed">
              {result.report}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}
