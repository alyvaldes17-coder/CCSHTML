import React from 'react'
import './Dashboard.css'

interface DashboardProps {
  email: string
  plan: string
}

export default function Dashboard({ email, plan }: DashboardProps) {
  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Nike Bot Commercial</h1>
        <div className="user-info">
          <span className="email">{email}</span>
          <span className={`plan-badge ${plan}`}>{plan.toUpperCase()}</span>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="section">
          <h2>Dashboard</h2>
          <p>Funcionalidad principal próximamente...</p>
          <p>Chat puedes ver tu engine.py aquí cuando esté integrado.</p>
        </div>
      </div>
    </div>
  )
}
