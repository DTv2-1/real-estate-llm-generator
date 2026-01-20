import React from 'react';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';

/**
 * Price details interface
 */
interface PriceDetails {
  display_price?: string;
  adult_price?: number;
  child_price?: number;
  group_price?: number;
  currency?: string;
}

/**
 * Props for TourPricing component
 */
interface TourPricingProps {
  /** Price details for the tour */
  priceDetails: PriceDetails;
}

/**
 * Component for displaying tour pricing information
 * Shows different price tiers (adult, child, group) and currency
 * 
 * @component
 */
export const TourPricing: React.FC<TourPricingProps> = ({ priceDetails }) => {
  const formatPrice = (price: number | undefined, currency: string = 'USD') => {
    if (!price) return null;
    return `${currency} ${price.toLocaleString()}`;
  };

  return (
    <SectionCard title="Precios" icon="💰">
      <FieldRenderer
        label="Precio Mostrado"
        value={priceDetails.display_price}
        type="currency"
        icon="💵"
      />
      <FieldRenderer
        label="Precio Adulto"
        value={formatPrice(priceDetails.adult_price, priceDetails.currency)}
        type="currency"
        icon="👤"
      />
      <FieldRenderer
        label="Precio Niño"
        value={formatPrice(priceDetails.child_price, priceDetails.currency)}
        type="currency"
        icon="👶"
      />
      <FieldRenderer
        label="Precio Grupo"
        value={formatPrice(priceDetails.group_price, priceDetails.currency)}
        type="currency"
        icon="👥"
      />
      <FieldRenderer label="Moneda" value={priceDetails.currency} icon="💱" />
    </SectionCard>
  );
};
