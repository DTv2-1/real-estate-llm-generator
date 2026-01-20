/**
 * usePropertyData Hook
 * 
 * Manages property data state and operations (CRUD)
 */

import { useState, useEffect } from 'react';
import type { PropertyData } from '../types';
import { 
  loadHistoryFromBackend, 
  loadPropertyFromHistory, 
  clearHistory 
} from '../services'

export const usePropertyData = () => {
  const [properties, setProperties] = useState<PropertyData[]>([])
  const [extractedProperty, setExtractedProperty] = useState<PropertyData | null>(null)
  const [showResults, setShowResults] = useState(false)
  const [confidence, setConfidence] = useState(0)
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(new Set())

  /**
   * Load property history from backend on mount
   */
  useEffect(() => {
    loadHistory()
  }, [])

  /**
   * Load property history
   */
  const loadHistory = async () => {
    try {
      const data = await loadHistoryFromBackend()
      setProperties(data)
    } catch (error) {
      console.error('Error loading history:', error)
    }
  }

  /**
   * Load a single property from history
   * @param propertyId - The property ID to load
   */
  const loadProperty = async (propertyId: string) => {
    try {
      const property = await loadPropertyFromHistory(propertyId)
      setExtractedProperty(property)
      setConfidence(property.extraction_confidence || 0.9)
      setShowResults(true)
      
      // Scroll to results section
      setTimeout(() => {
        document.getElementById('resultsSection')?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    } catch (error) {
      throw new Error('Error loading property: ' + (error as Error).message)
    }
  }

  /**
   * Clear all history with confirmation
   */
  const clearAllHistory = async () => {
    if (!confirm('Are you sure you want to delete all saved properties?')) {
      return
    }
    
    try {
      await clearHistory()
      alert('History cleared successfully')
      loadHistory()
    } catch (error) {
      alert('Error clearing history: ' + (error as Error).message)
    }
  }

  /**
   * Toggle collapsed state for a category group
   * @param category - Category key to toggle
   */
  const toggleGroup = (category: string) => {
    setCollapsedGroups(prev => {
      const newSet = new Set(prev)
      if (newSet.has(category)) {
        newSet.delete(category)
      } else {
        newSet.add(category)
      }
      return newSet
    })
  }

  /**
   * Reset form to initial state
   */
  const resetForm = () => {
    setShowResults(false)
    setExtractedProperty(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return {
    // State
    properties,
    extractedProperty,
    showResults,
    confidence,
    collapsedGroups,
    
    // Setters
    setExtractedProperty,
    setShowResults,
    setConfidence,
    
    // Actions
    loadHistory,
    loadProperty,
    clearAllHistory,
    toggleGroup,
    resetForm
  }
}
