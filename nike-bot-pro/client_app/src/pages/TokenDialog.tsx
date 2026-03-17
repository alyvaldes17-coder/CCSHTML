import React, { useState } from 'react'
import './TokenDialog.css'

interface TokenDialogProps {
  onSubmit: (token: string) => Promise<void>
}

export default function TokenDialog({ onSubmit }: TokenDialogProps) {
  const [token, setToken] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!token.trim()) {
      setError('Por favor ingresa un token')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      await onSubmit(token)
    } catch (err) {
      setError('Token inválido o expirado. Intenta de nuevo.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="token-dialog-container">
      <div className="token-dialog">
        <div className="dialog-header">
          <h1>Nike Bot Commercial</h1>
          <p>v1.0.0</p>
        </div>

        <form onSubmit={handleSubmit} className="token-form">
          <label htmlFor="token-input">Ingresa tu token de activación:</label>
          <textarea
            id="token-input"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="Pega aquí el token que recibiste por email..."
            rows={6}
            disabled={loading}
          />

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Validando...' : 'Activar'}
          </button>

          <div className="token-info">
            <p>¿No tienes token? Obtén uno en nuestro Discord.</p>
            <a href="#">Discord Community</a>
          </div>
        </form>
      </div>
    </div>
  )
}
