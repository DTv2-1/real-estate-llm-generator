import React from 'react';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';

/**
 * Props for TourInclusions component
 */
interface TourInclusionsProps {
  /** List of included items/services */
  inclusions?: string[];
  /** List of excluded items/services */
  exclusions?: string[];
}

/**
 * Component for displaying tour inclusions and exclusions
 * Shows what is and isn't included in the tour price
 * 
 * @component
 */
export const TourInclusions: React.FC<TourInclusionsProps> = ({
  inclusions,
  exclusions
}) => {
  return (
    <SectionCard title="Incluye / No Incluye" icon="📋">
      {inclusions && inclusions.length > 0 && (
        <div className="inclusions-section">
          <h4 className="subsection-title">✅ Incluye:</h4>
          <FieldRenderer
            label=""
            value=""
            type="list"
            listItems={inclusions}
          />
        </div>
      )}

      {exclusions && exclusions.length > 0 && (
        <div className="exclusions-section">
          <h4 className="subsection-title">❌ No Incluye:</h4>
          <FieldRenderer
            label=""
            value=""
            type="list"
            listItems={exclusions}
          />
        </div>
      )}
    </SectionCard>
  );
};
