import React from 'react';
import './InputSection.css';
import type { ContentType, CategoryConfig } from '../types';

/**
 * Props for the InputSection component
 */
interface InputSectionProps {
  /** Current URL being processed */
  url: string;
  /** Handler when URL changes */
  onUrlChange: (url: string) => void;
  /** Current content type selection */
  contentType: string;
  /** Handler when content type changes */
  onContentTypeChange: (type: string) => void;
  /** Available content types */
  availableContentTypes: ContentType[];
  /** Whether auto-detection is enabled */
  autoDetect: boolean;
  /** Handler to toggle auto-detection */
  onAutoDetectChange: (enabled: boolean) => void;
  /** Selected category for categorization */
  category: string;
  /** Handler when category changes */
  onCategoryChange: (category: string) => void;
  /** Available categories */
  categories: CategoryConfig[];
  /** Whether processing is in progress */
  isProcessing: boolean;
  /** Handler to submit form */
  onSubmit: () => void;
  /** Current tutorial step (if active) */
  tutorialStep?: number;
}

/**
 * Main input section for property data collection
 * Contains URL input, content type selector, category selector, and submit button
 * 
 * @component
 * @example
 * ```tsx
 * <InputSection
 *   url={currentUrl}
 *   onUrlChange={setUrl}
 *   contentType={selectedType}
 *   onContentTypeChange={setType}
 *   availableContentTypes={types}
 *   autoDetect={true}
 *   onAutoDetectChange={setAutoDetect}
 *   category="real-estate"
 *   onCategoryChange={setCategory}
 *   categories={categoryList}
 *   isProcessing={false}
 *   onSubmit={handleSubmit}
 * />
 * ```
 */
export const InputSection: React.FC<InputSectionProps> = ({
  url,
  onUrlChange,
  contentType,
  onContentTypeChange,
  availableContentTypes,
  autoDetect,
  onAutoDetectChange,
  category,
  onCategoryChange,
  categories,
  isProcessing,
  onSubmit,
  tutorialStep
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <section className="input-section">
      <form onSubmit={handleSubmit} className="input-form">
        <URLInput
          url={url}
          onChange={onUrlChange}
          isProcessing={isProcessing}
          tutorialStep={tutorialStep}
        />

        <ContentTypeSelector
          contentType={contentType}
          onChange={onContentTypeChange}
          availableContentTypes={availableContentTypes}
          autoDetect={autoDetect}
          onAutoDetectChange={onAutoDetectChange}
          tutorialStep={tutorialStep}
        />

        <CategorySelector
          category={category}
          onChange={onCategoryChange}
          categories={categories}
          tutorialStep={tutorialStep}
        />

        <SubmitButton
          isProcessing={isProcessing}
          disabled={!url.trim() || isProcessing}
          tutorialStep={tutorialStep}
        />
      </form>
    </section>
  );
};

/**
 * Props for URLInput component
 */
interface URLInputProps {
  /** Current URL value */
  url: string;
  /** Handler when URL changes */
  onChange: (url: string) => void;
  /** Whether processing is in progress */
  isProcessing: boolean;
  /** Current tutorial step */
  tutorialStep?: number;
}

/**
 * URL input field with icon and placeholder
 * 
 * @component
 */
export const URLInput: React.FC<URLInputProps> = ({
  url,
  onChange,
  isProcessing,
  tutorialStep
}) => {
  const isHighlighted = tutorialStep === 1;

  return (
    <div className={`input-group url-input-group ${isHighlighted ? 'tutorial-highlight' : ''}`}>
      <label htmlFor="url-input" className="input-label">
        <span className="label-icon">🔗</span>
        <span className="label-text">URL de la Propiedad</span>
      </label>
      <input
        id="url-input"
        type="url"
        value={url}
        onChange={(e) => onChange(e.target.value)}
        placeholder="https://ejemplo.com/propiedad/123"
        className="url-input"
        disabled={isProcessing}
        required
      />
    </div>
  );
};

/**
 * Props for ContentTypeSelector component
 */
interface ContentTypeSelectorProps {
  /** Current content type */
  contentType: string;
  /** Handler when content type changes */
  onChange: (type: string) => void;
  /** Available content types */
  availableContentTypes: ContentType[];
  /** Whether auto-detection is enabled */
  autoDetect: boolean;
  /** Handler to toggle auto-detection */
  onAutoDetectChange: (enabled: boolean) => void;
  /** Current tutorial step */
  tutorialStep?: number;
}

/**
 * Content type dropdown selector with auto-detection toggle
 * 
 * @component
 */
export const ContentTypeSelector: React.FC<ContentTypeSelectorProps> = ({
  contentType,
  onChange,
  availableContentTypes,
  autoDetect,
  onAutoDetectChange,
  tutorialStep
}) => {
  const isHighlighted = tutorialStep === 2;

  return (
    <div className={`input-group content-type-group ${isHighlighted ? 'tutorial-highlight' : ''}`}>
      <label htmlFor="content-type-select" className="input-label">
        <span className="label-icon">📋</span>
        <span className="label-text">Tipo de Contenido</span>
      </label>
      
      <div className="content-type-controls">
        <select
          id="content-type-select"
          value={contentType}
          onChange={(e) => onChange(e.target.value)}
          className="content-type-select"
          disabled={autoDetect}
        >
          <option value="">Seleccionar tipo...</option>
          {availableContentTypes.map((type) => (
            <option key={type.id || type.key} value={type.key}>
              {type.label}
            </option>
          ))}
        </select>

        <AutoDetectToggle
          autoDetect={autoDetect}
          onChange={onAutoDetectChange}
        />
      </div>
    </div>
  );
};

/**
 * Props for AutoDetectToggle component
 */
interface AutoDetectToggleProps {
  /** Whether auto-detection is enabled */
  autoDetect: boolean;
  /** Handler to toggle auto-detection */
  onChange: (enabled: boolean) => void;
}

/**
 * Toggle switch for automatic content type detection
 * 
 * @component
 */
export const AutoDetectToggle: React.FC<AutoDetectToggleProps> = ({
  autoDetect,
  onChange
}) => {
  return (
    <label className="auto-detect-toggle">
      <input
        type="checkbox"
        checked={autoDetect}
        onChange={(e) => onChange(e.target.checked)}
        className="toggle-checkbox"
      />
      <span className="toggle-label">Auto-detectar</span>
    </label>
  );
};

/**
 * Props for CategorySelector component
 */
interface CategorySelectorProps {
  /** Current category */
  category: string;
  /** Handler when category changes */
  onChange: (category: string) => void;
  /** Available categories */
  categories: CategoryConfig[];
  /** Current tutorial step */
  tutorialStep?: number;
}

/**
 * Category dropdown selector for property classification
 * 
 * @component
 */
export const CategorySelector: React.FC<CategorySelectorProps> = ({
  category,
  onChange,
  categories,
  tutorialStep
}) => {
  const isHighlighted = tutorialStep === 3;

  return (
    <div className={`input-group category-group ${isHighlighted ? 'tutorial-highlight' : ''}`}>
      <label htmlFor="category-select" className="input-label">
        <span className="label-icon">🏷️</span>
        <span className="label-text">Categoría</span>
      </label>
      <select
        id="category-select"
        value={category}
        onChange={(e) => onChange(e.target.value)}
        className="category-select"
      >
        <option value="">Auto (por URL)</option>
        {categories.map((cat) => (
          <option key={cat.id} value={cat.id}>
            {cat.name}
          </option>
        ))}
      </select>
    </div>
  );
};

/**
 * Props for SubmitButton component
 */
interface SubmitButtonProps {
  /** Whether processing is in progress */
  isProcessing: boolean;
  /** Whether button is disabled */
  disabled: boolean;
  /** Current tutorial step */
  tutorialStep?: number;
}

/**
 * Submit button to trigger property processing
 * Shows loading state during processing
 * 
 * @component
 */
export const SubmitButton: React.FC<SubmitButtonProps> = ({
  isProcessing,
  disabled,
  tutorialStep
}) => {
  const isHighlighted = tutorialStep === 4;

  return (
    <button
      type="submit"
      className={`submit-button ${isHighlighted ? 'tutorial-highlight' : ''}`}
      disabled={disabled}
    >
      {isProcessing ? (
        <>
          <span className="spinner">⏳</span>
          <span>Procesando...</span>
        </>
      ) : (
        <>
          <span className="button-icon">🚀</span>
          <span>Procesar Propiedad</span>
        </>
      )}
    </button>
  );
};
