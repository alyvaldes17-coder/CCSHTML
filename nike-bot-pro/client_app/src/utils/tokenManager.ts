import axios from 'axios'

export interface TokenValidationResult {
  valid: boolean
  email?: string
  plan?: string
  expires?: number
}

export class TokenManager {
  private apiUrl: string = 'https://nike-bot-pro-production.up.railway.app'

  async validateToken(token?: string): Promise<TokenValidationResult | null> {
    try {
      if (!token) {
        // Load from localStorage
        token = localStorage.getItem('nike_bot_token')
      }

      if (!token) {
        return null
      }

      // Try online validation with correct endpoint
      try {
        const response = await axios.get(`${this.apiUrl}/auth/validate`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'X-HWID': '00000000-0000-0000-0000-000000000000'
          },
          timeout: 5000
        })

        if (response.status === 200) {
          return response.data
        }
      } catch (err) {
        // Fallback to offline validation
        return this.validateTokenOffline(token)
      }
    } catch (error) {
      console.error('Token validation error:', error)
      return null
    }
  }

  async saveToken(token: string): Promise<boolean> {
    try {
      // Validate first
      const result = await this.validateToken(token)
      
      if (result && result.valid) {
        localStorage.setItem('nike_bot_token', token)
        return true
      }

      return false
    } catch (error) {
      console.error('Save token error:', error)
      return false
    }
  }

  validateTokenOffline(token: string): TokenValidationResult | null {
    try {
      // Decode JWT without verification (client-side only)
      const parts = token.split('.')
      if (parts.length !== 3) {
        return null
      }

      const payload = JSON.parse(
        atob(parts[1].replace(/-/g, '+').replace(/_/g, '/'))
      )

      // Check expiry
      const expTime = new Date(payload.exp * 1000)
      if (expTime < new Date()) {
        return null
      }

      return {
        valid: true,
        email: payload.email,
        plan: payload.plan,
        expires: payload.exp,
      }
    } catch (error) {
      console.error('Offline validation error:', error)
      return null
    }
  }

  checkExpiry(token?: string): { daysRemaining: number; expiresSoon: boolean } | null {
    try {
      if (!token) {
        token = localStorage.getItem('nike_bot_token')
      }

      if (!token) {
        return null
      }

      const parts = token.split('.')
      const payload = JSON.parse(
        atob(parts[1].replace(/-/g, '+').replace(/_/g, '/'))
      )

      const expTime = new Date(payload.exp * 1000)
      const now = new Date()
      const daysRemaining = Math.floor(
        (expTime.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
      )

      return {
        daysRemaining: Math.max(0, daysRemaining),
        expiresSoon: daysRemaining <= 3,
      }
    } catch (error) {
      return null
    }
  }

  revokeToken(): void {
    localStorage.removeItem('nike_bot_token')
  }
}
