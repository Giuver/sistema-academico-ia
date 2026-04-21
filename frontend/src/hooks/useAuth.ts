import { useState, useEffect } from 'react'
import { supabase } from '@/services/supabase'
import { User, Session } from '@supabase/supabase-js'

interface AuthState {
  user: User | null
  session: Session | null
  loading: boolean
  perfil: any | null
}

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    session: null,
    loading: true,
    perfil: null,
  })

  useEffect(() => {
    // Obtener sesión inicial
    supabase.auth.getSession().then(({ data: { session } }) => {
      setAuthState(prev => ({
        ...prev,
        session,
        user: session?.user || null,
        loading: false,
      }))

      if (session?.user) {
        cargarPerfil(session.user.id)
      }
    })

    // Escuchar cambios de autenticación
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setAuthState(prev => ({
        ...prev,
        session,
        user: session?.user || null,
      }))

      if (session?.user) {
        cargarPerfil(session.user.id)
      } else {
        setAuthState(prev => ({ ...prev, perfil: null }))
      }
    })

    return () => subscription.unsubscribe()
  }, [])

  const cargarPerfil = async (userId: string) => {
    const { data, error } = await supabase
      .from('perfiles')
      .select('*')
      .eq('id', userId)
      .single()

    if (data && !error) {
      setAuthState(prev => ({ ...prev, perfil: data }))
    }
  }

  const signIn = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    return { data, error }
  }

  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    return { error }
  }

  return {
    ...authState,
    signIn,
    signOut,
    isAdmin: authState.perfil?.rol === 'admin',
    isDirector: authState.perfil?.rol === 'director',
    isDocente: authState.perfil?.rol === 'docente',
    isConsulta: authState.perfil?.rol === 'consulta',
  }
}
