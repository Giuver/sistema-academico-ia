import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('es-PE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export function formatDateTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('es-PE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function getNivelRiesgoColor(nivel: string): string {
  switch (nivel.toLowerCase()) {
    case 'alto':
    case 'critica':
      return 'text-red-600 bg-red-50'
    case 'medio':
    case 'moderada':
      return 'text-yellow-600 bg-yellow-50'
    case 'bajo':
    case 'preventiva':
      return 'text-blue-600 bg-blue-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

export function getNotaColor(nota: number): string {
  if (nota >= 18) return 'text-green-700'
  if (nota >= 14) return 'text-blue-600'
  if (nota >= 11) return 'text-yellow-600'
  return 'text-red-600'
}

export function calcularPromedio(notas: number[]): number {
  if (notas.length === 0) return 0
  return notas.reduce((sum, nota) => sum + nota, 0) / notas.length
}

export function formatPorcentaje(valor: number): string {
  return `${(valor * 100).toFixed(1)}%`
}
