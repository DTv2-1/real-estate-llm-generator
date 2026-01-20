/**
 * useIngestionStats Hook
 * 
 * Manages ingestion statistics and recent properties
 */

import { useState, useEffect } from 'react';
import type { RecentProperty, WebsiteConfig } from '../types';
import { loadIngestionStats, loadSupportedWebsites } from '../services'

export const useIngestionStats = () => {
  const [propertiesProcessedToday, setPropertiesProcessedToday] = useState<number>(0)
  const [recentProperties, setRecentProperties] = useState<RecentProperty[]>([])
  const [supportedWebsites, setSupportedWebsites] = useState<WebsiteConfig[]>([])
  const [websitesLoading, setWebsitesLoading] = useState(true)

  /**
   * Load statistics on mount
   */
  useEffect(() => {
    loadStats()
    loadWebsites()
  }, [])

  /**
   * Load ingestion statistics
   */
  const loadStats = async () => {
    try {
      const data = await loadIngestionStats()
      setPropertiesProcessedToday(data.properties_today || 0)
      setRecentProperties(data.recent_properties || [])
    } catch (error) {
      console.error('Error loading ingestion stats:', error)
    }
  }

  /**
   * Load supported websites
   */
  const loadWebsites = async () => {
    try {
      const websites = await loadSupportedWebsites()
      setSupportedWebsites(websites)
      setWebsitesLoading(false)
    } catch (error) {
      console.error('Error loading supported websites:', error)
      setWebsitesLoading(false)
    }
  }

  /**
   * Reload statistics (useful after processing a property)
   */
  const reloadStats = async () => {
    await loadStats()
  }

  return {
    propertiesProcessedToday,
    recentProperties,
    supportedWebsites,
    websitesLoading,
    loadStats,
    reloadStats
  }
}
