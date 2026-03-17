import './App.css'
import { useState, useEffect } from 'react'
import TokenDialog from './pages/TokenDialog'
import Dashboard from './pages/Dashboard'
import { TokenManager } from './utils/tokenManager'

function App() {
  const [authenticated, setAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [userEmail, setUserEmail] = useState('')
  const [userPlan, setUserPlan] = useState('')

  useEffect(() => {
    checkAuthentication()
  }, [])

  const checkAuthentication = async () => {
    const tokenMgr = new TokenManager()
    const result = await tokenMgr.validateToken()
    
    if (result && result.valid) {
      setAuthenticated(true)
      setUserEmail(result.email || '')
      setUserPlan(result.plan || '')
    } else {
      setAuthenticated(false)
    }
    setLoading(false)
  }

  const handleTokenSubmit = async (token: string) => {
    const tokenMgr = new TokenManager()
    const tokenMgr = new TokenManager() 
    const saved = await tokenMgr.saveToken(token)
    
    if (saved) {
      const result = await tokenMgr.validateToken(token)
      if (result && result.valid) {
        setAuthenticated(true)
        setUserEmail(result.email || '')
        setUserPlan(result.plan || '')
      }
    }
  }

  if (loading) {
    return <div className="loading">Iniciando...</div>
  }

  return (
    <>
      {!authenticated ? (
        <TokenDialog onSubmit={handleTokenSubmit} />
      ) : (
        <Dashboard email={userEmail} plan={userPlan} />
      )}
    </>
  )
}

export default App
