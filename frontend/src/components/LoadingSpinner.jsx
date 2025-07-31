/**
 * ⏳ LoadingSpinner Component
 * 
 * Componente de loading spinner reutilizável
 */

import React from 'react'
import { motion } from 'framer-motion'

const LoadingSpinner = ({ 
  size = 'md', 
  color = 'blue', 
  text = '', 
  className = '',
  fullScreen = false 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  }

  const colorClasses = {
    blue: 'border-blue-500',
    green: 'border-green-500',
    yellow: 'border-yellow-500',
    red: 'border-red-500',
    purple: 'border-purple-500',
    gray: 'border-gray-500',
    white: 'border-white'
  }

  const spinner = (
    <motion.div
      className={`
        ${sizeClasses[size]} 
        border-2 
        ${colorClasses[color]} 
        border-t-transparent 
        rounded-full 
        ${className}
      `}
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: 'linear'
      }}
    />
  )

  const content = (
    <div className="flex flex-col items-center justify-center space-y-3">
      {spinner}
      {text && (
        <motion.p
          className="text-sm text-gray-400 font-medium"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {text}
        </motion.p>
      )}
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center z-50">
        <div className="bg-gray-800 rounded-lg p-8 shadow-xl">
          {content}
        </div>
      </div>
    )
  }

  return content
}

export default LoadingSpinner
