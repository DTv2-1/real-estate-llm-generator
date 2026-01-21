import React, { useState } from 'react';
import './DataCollector.css';
import type { PropertyData } from './types';

// Import all extracted modules
import { usePropertyData } from './hooks/usePropertyData';
import { useContentTypes } from './hooks/useContentTypes';
import { useIngestionStats } from './hooks/useIngestionStats';
import { useTutorial } from './hooks/useTutorial';
import { processProperty, savePropertyViaIngestion } from './services/ingestionService';
import { getCategoryFromUrl } from './utils/categoryUtils';
import { validateUrl } from './utils/validators';

// Import UI Section Components
import {
  Sidebar,
  InputSection,
  RecentProperties,
  LoadingSection,
  ResultsSection
} from './sections';

// Import Content Type Templates
import {
  RealEstateTemplate,
  TourTemplate,
  RestaurantTemplate,
  TransportationTemplate,
  LocalTipsTemplate
} from './contentTypes';

// Import Progress WebSocket hook
import { useProgressWebSocket } from '../../hooks/useProgressWebSocket';

/**
 * Main DataCollector component - orchestrates all functionality
 * Integrates property data management, content types, statistics, and UI sections
 * 
 * @component
 */
export const DataCollector: React.FC = () => {
  // ============================================================================
  // State Management - Using Custom Hooks
  // ============================================================================
  
  const {
    properties,
    loadHistory,
    loadProperty,
  } = usePropertyData();

  const {
    contentTypes,
    selectedContentType,
    setSelectedContentType,
  } = useContentTypes();

  const {
    propertiesProcessedToday,
    recentProperties,
  } = useIngestionStats();

  const {
    tutorialStep,
    startTutorial,
  } = useTutorial();

  // ============================================================================
  // Local UI State
  // ============================================================================
  
  const [url, setUrl] = useState('');
  const [category, setCategory] = useState('');
  const [autoDetect, setAutoDetect] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [showRawData, setShowRawData] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [extractedProperty, setExtractedProperty] = useState<any>(null);
  const [isTutorialActive, setIsTutorialActive] = useState(false);
  const [isSavingToDb, setIsSavingToDb] = useState(false);
  
  // Use empty array for categories (not provided by hook)
  const categories: any[] = [];

  // ============================================================================
  // WebSocket Progress Tracking
  // ============================================================================
  
  const { progress, isConnected, connect, disconnect, reset } = useProgressWebSocket({
    onComplete: (data) => {
      console.log('✅ Processing complete:', data);
      
      if (data && data.property) {
        const propertyWithMetadata = {
          ...data.property,
          content_type: data.content_type,
          content_type_confidence: data.content_type_confidence,
          page_type: data.page_type,
          timestamp: new Date().toISOString()
        };
        
        setExtractedProperty(propertyWithMetadata);
        setShowResults(true);
      }
      
      setLoading(false);
      reset();
    },
    onError: (errorMsg) => {
      console.error('❌ Processing error:', errorMsg);
      setError(errorMsg);
      setLoading(false);
      reset();
    }
  });

  // ============================================================================
  // Event Handlers
  // ============================================================================

  /**
   * Handle URL input changes
   */
  const handleUrlChange = (newUrl: string) => {
    setUrl(newUrl);
    setError('');
    
    // Auto-detect category from URL if no manual selection
    if (!category && newUrl) {
      const detectedCategory = getCategoryFromUrl(newUrl);
      if (detectedCategory) {
        setCategory(detectedCategory);
      }
    }
  };

  /**
   * Handle form submission and property processing
   */
  const handleSubmit = async () => {
    // Validation
    if (!url.trim()) {
      setError('Por favor ingresa una URL válida');
      return;
    }

    if (!validateUrl(url)) {
      setError('La URL ingresada no es válida');
      return;
    }

    // Reset state
    setError('');
    setLoading(true);
    setShowResults(false);
    setExtractedProperty(null);

    try {
      // Determine content type
      const contentTypeToUse = autoDetect ? 'auto' : selectedContentType;

      // Process property - service expects (inputType, value, contentType)
      const result = await processProperty(
        'url',  // inputType
        url,    // value
        contentTypeToUse || 'real-estate'  // contentType
      );

      // Handle result
      if (result && result.task_id) {
        // Connect WebSocket for progress tracking
        console.log('🔌 Connecting WebSocket with task_id:', result.task_id);
        connect(result.task_id);
      } else if (result && result.property) {
        // Direct response without WebSocket
        setExtractedProperty(result.property);
        setShowResults(true);
        setLoading(false);
      }
    } catch (err: any) {
      console.error('Error processing property:', err);
      setError(err.message || 'Error al procesar la propiedad');
      setLoading(false);
      disconnect();
    }
  };

  /**
   * Handle saving property to Google Sheets
   */
  const handleSaveProperty = async () => {
    if (!extractedProperty) return;

    try {
      // TODO: Implement save to Google Sheets
      console.log('Saving property:', extractedProperty);
      // Reload history and stats after saving
      loadHistory();
    } catch (err: any) {
      setError(err.message || 'Error al guardar la propiedad');
    }
  };

  /**
   * Handle saving property to PostgreSQL database
   */
  const handleSaveToDatabase = async () => {
    if (!extractedProperty) return;

    setIsSavingToDb(true);
    try {
      // Use the service layer instead of direct fetch
      const savedProperty = await savePropertyViaIngestion(extractedProperty);
      
      console.log('✅ Propiedad guardada en BD:', savedProperty);
      
      // Reload history and stats after saving
      loadHistory();
      
      // Show success message (optional)
      alert('✅ Contenido guardado exitosamente en la base de datos');
    } catch (err: any) {
      console.error('❌ Error saving to database:', err);
      setError(err.message || 'Error al guardar en la base de datos');
      alert('❌ Error al guardar: ' + (err.message || 'Error desconocido'));
    } finally {
      setIsSavingToDb(false);
    }
  };

  /**
   * Handle exporting property as JSON
   */
  const handleExportProperty = () => {
    if (!extractedProperty) return;

    const dataStr = JSON.stringify(extractedProperty, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `property-${extractedProperty.id || 'export'}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  /**
   * Handle selecting a property from history
   */
  const handleSelectProperty = async (property: any) => {
    if (property.id) {
      await loadProperty(property.id);
      setExtractedProperty(property);
      setShowResults(true);
    } else {
      setExtractedProperty(property);
      setShowResults(true);
    }
  };

  /**
   * Toggle sidebar collapse state
   */
  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  /**
   * Toggle raw data view
   */
  const toggleRawData = () => {
    setShowRawData(!showRawData);
  };
  
  /**
   * Handle tutorial actions
   */
  const handleStartTutorial = () => {
    setIsTutorialActive(true);
    startTutorial();
  };
  
  const handleCloseTutorial = () => {
    setIsTutorialActive(false);
  };

  // ============================================================================
  // Helper Functions
  // ============================================================================

  /**
   * Convert RecentProperty to PropertyData format for display
   */
  const convertRecentToPropertyData = (recent: typeof recentProperties): PropertyData[] => {
    return recent.map(prop => ({
      id: prop.id,
      title: prop.title,
      location: prop.location,
      price_usd: prop.price_usd,
      bedrooms: prop.bedrooms,
      bathrooms: prop.bathrooms,
      source_website: prop.source_website,
      created_at: prop.created_at,
      content_type: 'real-estate', // Default for recent properties
    } as PropertyData))
  }

  /**
   * Group properties by category for sidebar
   */
  const groupPropertiesByCategory = () => {
    const grouped: Record<string, any[]> = {};
    
    properties.forEach(prop => {
      const cat = prop.category || 'Sin categoría';
      if (!grouped[cat]) {
        grouped[cat] = [];
      }
      grouped[cat].push(prop);
    });

    return grouped;
  };

  /**
   * Render content-specific template based on content type
   */
  const renderContentTemplate = () => {
    if (!extractedProperty) return null;

    const contentType = extractedProperty.content_type || 'real-estate';

    switch (contentType) {
      case 'real-estate':
        return <RealEstateTemplate property={extractedProperty} />;
      case 'tour':
      case 'activity':
        return <TourTemplate property={extractedProperty} />;
      case 'restaurant':
        return <RestaurantTemplate property={extractedProperty} />;
      case 'transportation':
        return <TransportationTemplate property={extractedProperty} />;
      case 'local-tips':
        return <LocalTipsTemplate property={extractedProperty} />;
      default:
        // Fallback to real estate template
        return <RealEstateTemplate property={extractedProperty} />;
    }
  };

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <div className="data-collector">
      <div className="data-collector-content">
        {/* Sidebar with property history */}
        <Sidebar
          isCollapsed={isSidebarCollapsed}
          onToggle={toggleSidebar}
          propertiesByCategory={groupPropertiesByCategory()}
          onSelectProperty={handleSelectProperty}
          selectedPropertyId={extractedProperty?.id}
        />

        <main className="data-collector-main">
          {/* Input Section - Only show when no results */}
          {!showResults && (
            <InputSection
              url={url}
              onUrlChange={handleUrlChange}
              contentType={selectedContentType}
              onContentTypeChange={setSelectedContentType}
              availableContentTypes={contentTypes}
              autoDetect={autoDetect}
              onAutoDetectChange={setAutoDetect}
              category={category}
              onCategoryChange={setCategory}
              categories={categories}
              isProcessing={loading}
              onSubmit={handleSubmit}
              tutorialStep={isTutorialActive ? tutorialStep || 0 : undefined}
            />
          )}

          {/* Error Message */}
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              <span className="error-text">{error}</span>
              <button
                onClick={() => setError('')}
                className="error-dismiss"
                aria-label="Dismiss error"
              >
                ✕
              </button>
            </div>
          )}

          {/* Recent Properties Grid */}
          {!loading && !showResults && recentProperties.length > 0 && (
            <RecentProperties
              properties={convertRecentToPropertyData(recentProperties)}
              onSelectProperty={handleSelectProperty}
              selectedPropertyId={extractedProperty?.id}
              maxItems={6}
            />
          )}

          {/* Loading Section */}
          {loading && (
            <LoadingSection
              message={progress?.status || "Procesando contenido..."}
              progress={progress?.progress}
              statusMessages={progress?.stage ? [progress.stage] : []}
              showSpinner={true}
            />
          )}

          {/* Results Section */}
          {showResults && extractedProperty && (
            <ResultsSection
              property={extractedProperty}
              showRawData={showRawData}
              onToggleRawData={toggleRawData}
              onSave={handleSaveProperty}
              onSaveToDatabase={handleSaveToDatabase}
              onExport={handleExportProperty}
              onNewSearch={() => {
                setShowResults(false);
                setExtractedProperty(null);
                setUrl('');
              }}
              isSaving={false}
              isSavingToDb={isSavingToDb}
              tutorialStep={isTutorialActive ? tutorialStep || 0 : undefined}
            />
          )}
        </main>
      </div>

      {/* Tutorial Overlay */}
      {isTutorialActive && tutorialStep && (
        <div className="tutorial-overlay">
          <div className="tutorial-content">
            <h3>Tutorial - Paso {tutorialStep} de 6</h3>
            <p>Sigue los pasos resaltados para aprender a usar el recolector.</p>
            <div className="tutorial-actions">
              <button onClick={handleCloseTutorial} className="tutorial-button primary">
                Cerrar Tutorial
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Default export for backward compatibility
export default DataCollector;
