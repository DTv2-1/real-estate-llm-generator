/**
 * useContentTypes Hook
 * 
 * Manages content types state and loading
 */

import { useState, useEffect } from 'react';
import type { ContentType } from '../types';
import { loadContentTypes } from '../services'

export const useContentTypes = () => {
  const [contentTypes, setContentTypes] = useState<ContentType[]>([])
  const [selectedContentType, setSelectedContentType] = useState('auto')

  /**
   * Load content types from backend on mount
   */
  useEffect(() => {
    fetchContentTypes()
  }, [])

  /**
   * Fetch content types from API
   */
  const fetchContentTypes = async () => {
    try {
      const types = await loadContentTypes()
      setContentTypes(types)
    } catch (error) {
      console.error('Error loading content types:', error)
    }
  }

  /**
   * Reset content type selection to auto
   */
  const resetContentType = () => {
    setSelectedContentType('auto')
  }

  return {
    contentTypes,
    selectedContentType,
    setSelectedContentType,
    fetchContentTypes,
    resetContentType
  }
}
