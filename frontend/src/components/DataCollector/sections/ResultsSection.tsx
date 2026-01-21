import React from 'react';
import './ResultsSection.css';
import type { PropertyData } from '../types';
import {
  formatPrice,
  formatDate,
  formatArea,
  formatBoolean
} from '../utils/formatters';
import {
  RealEstateTemplate,
  TourTemplate,
  RestaurantTemplate,
  TransportationTemplate,
  LocalTipsTemplate
} from '../contentTypes';

/**
 * Props for ResultsSection component
 */
interface ResultsSectionProps {
  /** Property data to display */
  property: PropertyData | null;
  /** Whether to show raw JSON view */
  showRawData: boolean;
  /** Handler to toggle raw data view */
  onToggleRawData: () => void;
  /** Handler to save property to Google Sheets */
  onSave: () => void;
  /** Handler to save property to database */
  onSaveToDatabase: () => void;
  /** Handler to export property */
  onExport: () => void;
  /** Whether save operation is in progress */
  isSaving: boolean;
  /** Whether database save is in progress */
  isSavingToDb: boolean;
  /** Handler to start new search */
  onNewSearch?: () => void;
  /** Current tutorial step */
  tutorialStep?: number;
}

/**
 * Results section displaying extracted property data
 * Shows formatted fields, images, and action buttons
 * 
 * @component
 * @example
 * ```tsx
 * <ResultsSection
 *   property={extractedProperty}
 *   showRawData={false}
 *   onToggleRawData={toggleRaw}
 *   onSave={handleSave}
 *   onExport={handleExport}
 *   isSaving={false}
 * />
 * ```
 */
export const ResultsSection: React.FC<ResultsSectionProps> = ({
  property,
  showRawData,
  onToggleRawData,
  onSave,
  onSaveToDatabase,
  onExport,
  isSaving,
  isSavingToDb,
  onNewSearch,
  tutorialStep
}) => {
  if (!property) {
    return null;
  }

  return (
    <section className="results-section">
      <ResultsHeader
        onToggleRawData={onToggleRawData}
        showRawData={showRawData}
        onNewSearch={onNewSearch}
        tutorialStep={tutorialStep}
      />

      <div className="results-content">
        {showRawData ? (
          <RawDataView property={property} />
        ) : (
          <PropertyDataView property={property} />
        )}
      </div>

      <ResultsActions
        onSave={onSave}
        onSaveToDatabase={onSaveToDatabase}
        onExport={onExport}
        isSaving={isSaving}
        isSavingToDb={isSavingToDb}
        tutorialStep={tutorialStep}
      />
    </section>
  );
};

/**
 * Props for ResultsHeader component
 */
interface ResultsHeaderProps {
  /** Handler to toggle raw data view */
  onToggleRawData: () => void;
  /** Whether raw data is currently shown */
  showRawData: boolean;
  /** Handler to start new search */
  onNewSearch?: () => void;
  /** Current tutorial step */
  tutorialStep?: number;
}

/**
 * Header for results section with title and view toggle
 * 
 * @component
 */
export const ResultsHeader: React.FC<ResultsHeaderProps> = ({
  onToggleRawData,
  showRawData,
  onNewSearch,
  tutorialStep
}) => {
  const isHighlighted = tutorialStep === 5;

  return (
    <div className={`results-header ${isHighlighted ? 'tutorial-highlight' : ''}`}>
      <h2 className="results-title">
        <span className="title-icon">✨</span>
        Datos Extraídos
      </h2>
      <div className="header-actions">
        {onNewSearch && (
          <button
            onClick={onNewSearch}
            className="new-search-button"
            aria-label="Nueva búsqueda"
          >
            ← Nueva Búsqueda
          </button>
        )}
        <button
          onClick={onToggleRawData}
          className="toggle-view-button"
          aria-label={showRawData ? 'Ver datos formateados' : 'Ver JSON completo'}
        >
          {showRawData ? '📋 Vista Formateada' : '🔍 Ver JSON'}
        </button>
      </div>
    </div>
  );
};

/**
 * Props for RawDataView component
 */
interface RawDataViewProps {
  /** Property data to display as JSON */
  property: PropertyData;
}

/**
 * Raw JSON view of property data with syntax highlighting
 * 
 * @component
 */
export const RawDataView: React.FC<RawDataViewProps> = ({ property }) => {
  const jsonString = JSON.stringify(property, null, 2);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(jsonString);
  };

  return (
    <div className="raw-data-view">
      <div className="raw-data-header">
        <span className="data-size">
          {jsonString.length} caracteres
        </span>
        <button
          onClick={copyToClipboard}
          className="copy-button"
          title="Copiar JSON"
        >
          📋 Copiar
        </button>
      </div>
      <pre className="json-viewer">
        <code>{jsonString}</code>
      </pre>
    </div>
  );
};

/**
 * Props for PropertyDataView component
 */
interface PropertyDataViewProps {
  /** Property data to display */
  property: PropertyData;
}

/**
 * Formatted view of property data organized in sections
 * Displays all fields in a user-friendly layout using content-specific templates
 * 
 * @component
 */
export const PropertyDataView: React.FC<PropertyDataViewProps> = ({ property }) => {
  // Use content-specific template if available
  const contentType = property.content_type?.toLowerCase();
  
  switch (contentType) {
    case 'real_estate':
    case 'realestate':
      return <RealEstateTemplate property={property} />;
    
    case 'tour':
    case 'activity':
      return <TourTemplate property={property} />;
    
    case 'restaurant':
    case 'dining':
      return <RestaurantTemplate property={property} />;
    
    case 'transportation':
    case 'transport':
      return <TransportationTemplate property={property} />;
    
    case 'local_tips':
    case 'localtips':
    case 'tips':
      return <LocalTipsTemplate property={property} />;
    
    default:
      // Fallback to generic view for unknown content types
      return <GenericDataView property={property} />;
  }
};

/**
 * Props for GenericDataView component
 */
interface GenericDataViewProps {
  /** Property data to display */
  property: PropertyData;
}

/**
 * Generic fallback view for content types without specific templates
 * 
 * @component
 */
export const GenericDataView: React.FC<GenericDataViewProps> = ({ property }) => {
  return (
    <>
      {/* Basic Information */}
      <section className="data-section">
        <h3 className="section-title">📝 Información Básica</h3>
        <div className="data-grid">
          <DataField label="Título" value={property.title} />
          <DataField label="URL" value={property.url} type="url" />
          <DataField label="Tipo de Contenido" value={property.content_type} />
          <DataField label="Categoría" value={property.category} />
        </div>
      </section>

      {/* Price Information */}
      {property.price_details && (
        <section className="data-section">
          <h3 className="section-title">💰 Información de Precio</h3>
          <div className="data-grid">
            <DataField
              label="Precio de Venta"
              value={property.price_details.sale_price ? formatPrice(property.price_details.sale_price) : null}
            />
            <DataField
              label="Precio de Renta"
              value={property.price_details.rental_price ? formatPrice(property.price_details.rental_price) : null}
            />
            <DataField label="Precio Mostrado" value={property.price_details.display_price} />
            <DataField label="Moneda" value={property.price_details.currency} />
          </div>
        </section>
      )}

      {/* Location */}
      {property.location && typeof property.location === 'object' && (
        <section className="data-section">
          <h3 className="section-title">📍 Ubicación</h3>
          <div className="data-grid">
            <DataField label="Dirección" value={property.location.address} />
            <DataField label="Ciudad" value={property.location.city} />
            <DataField label="Estado/Provincia" value={property.location.state} />
            <DataField label="País" value={property.location.country} />
            <DataField label="Código Postal" value={property.location.postal_code} />
          </div>
        </section>
      )}

      {/* Property Details */}
      {property.details && (
        <section className="data-section">
          <h3 className="section-title">🏠 Detalles de la Propiedad</h3>
          <div className="data-grid">
            <DataField label="Tipo de Propiedad" value={property.details.property_type} />
            <DataField label="Habitaciones" value={property.details.bedrooms} />
            <DataField label="Baños" value={property.details.bathrooms} />
            <DataField
              label="Área"
              value={property.details.area ? formatArea(property.details.area, property.details.area_unit) : null}
            />
            <DataField label="Año de Construcción" value={property.details.year_built} />
            <DataField
              label="Amueblado"
              value={formatBoolean(property.details.furnished)}
            />
          </div>
        </section>
      )}

      {/* Description */}
      {property.description && (
        <section className="data-section">
          <h3 className="section-title">📄 Descripción</h3>
          <div className="description-text">{property.description}</div>
        </section>
      )}

      {/* Features */}
      {property.features && property.features.length > 0 && (
        <section className="data-section">
          <h3 className="section-title">⭐ Características</h3>
          <ul className="features-list">
            {property.features.map((feature: string, index: number) => (
              <li key={index} className="feature-item">
                {feature}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Images */}
      {property.images && property.images.length > 0 && (
        <section className="data-section">
          <h3 className="section-title">📷 Imágenes ({property.images.length})</h3>
          <div className="images-grid">
            {property.images.slice(0, 6).map((imageUrl: string, index: number) => (
              <div key={index} className="image-thumbnail">
                <img src={imageUrl} alt={`Imagen ${index + 1}`} loading="lazy" />
              </div>
            ))}
          </div>
          {property.images.length > 6 && (
            <p className="images-count">
              +{property.images.length - 6} imágenes más
            </p>
          )}
        </section>
      )}

      {/* Contact */}
      {property.contact && (
        <section className="data-section">
          <h3 className="section-title">📞 Contacto</h3>
          <div className="data-grid">
            <DataField label="Nombre" value={property.contact.name} />
            <DataField label="Email" value={property.contact.email} type="email" />
            <DataField label="Teléfono" value={property.contact.phone} type="tel" />
            <DataField label="WhatsApp" value={property.contact.whatsapp} type="tel" />
          </div>
        </section>
      )}

      {/* Metadata */}
      <section className="data-section metadata-section">
        <h3 className="section-title">ℹ️ Metadatos</h3>
        <div className="data-grid">
          <DataField label="ID" value={property.id} />
          <DataField
            label="Fecha de Extracción"
            value={property.timestamp ? formatDate(property.timestamp) : null}
          />
          <DataField label="Procesado por" value={property.processed_by} />
        </div>
      </section>
    </>
  );
};

/**
 * Props for DataField component
 */
interface DataFieldProps {
  /** Field label */
  label: string;
  /** Field value */
  value: string | number | null | undefined;
  /** Field type for special formatting */
  type?: 'text' | 'url' | 'email' | 'tel';
}

/**
 * Individual data field with label and value
 * Handles different value types and displays appropriately
 * 
 * @component
 */
export const DataField: React.FC<DataFieldProps> = ({
  label,
  value,
  type = 'text'
}) => {
  if (value === null || value === undefined || value === '') {
    return null;
  }

  const renderValue = () => {
    const stringValue = String(value);

    switch (type) {
      case 'url':
        return (
          <a
            href={stringValue}
            target="_blank"
            rel="noopener noreferrer"
            className="field-link"
          >
            {stringValue}
          </a>
        );
      case 'email':
        return (
          <a href={`mailto:${stringValue}`} className="field-link">
            {stringValue}
          </a>
        );
      case 'tel':
        return (
          <a href={`tel:${stringValue}`} className="field-link">
            {stringValue}
          </a>
        );
      default:
        return <span className="field-value">{stringValue}</span>;
    }
  };

  return (
    <div className="data-field">
      <span className="field-label">{label}:</span>
      {renderValue()}
    </div>
  );
};

/**
 * Props for ResultsActions component
 */
interface ResultsActionsProps {
  /** Handler to save property to Google Sheets */
  onSave: () => void;
  /** Handler to save property to database */
  onSaveToDatabase: () => void;
  /** Handler to export property */
  onExport: () => void;
  /** Whether Google Sheets save is in progress */
  isSaving: boolean;
  /** Whether database save is in progress */
  isSavingToDb: boolean;
  /** Current tutorial step */
  tutorialStep?: number;
}

/**
 * Action buttons for results section
 * Provides save and export functionality
 * 
 * @component
 */
export const ResultsActions: React.FC<ResultsActionsProps> = ({
  onSave,
  onSaveToDatabase,
  onExport,
  isSaving,
  isSavingToDb,
  tutorialStep
}) => {
  const isHighlighted = tutorialStep === 6;

  return (
    <div className={`results-actions ${isHighlighted ? 'tutorial-highlight' : ''}`}>
      <button
        onClick={onSaveToDatabase}
        className="action-button save-db-button"
        disabled={isSavingToDb || isSaving}
      >
        {isSavingToDb ? (
          <>
            <span className="spinner">⏳</span>
            <span>Guardando...</span>
          </>
        ) : (
          <>
            <span className="button-icon">🗄️</span>
            <span>Guardar en Base de Datos</span>
          </>
        )}
      </button>

      <button
        onClick={onSave}
        className="action-button save-button"
        disabled={isSaving || isSavingToDb}
      >
        {isSaving ? (
          <>
            <span className="spinner">⏳</span>
            <span>Guardando...</span>
          </>
        ) : (
          <>
            <span className="button-icon">💾</span>
            <span>Guardar en Google Sheets</span>
          </>
        )}
      </button>

      <button
        onClick={onExport}
        className="action-button export-button"
        disabled={isSaving || isSavingToDb}
      >
        <span className="button-icon">📥</span>
        <span>Exportar JSON</span>
      </button>
    </div>
  );
};
