import React from 'react';
import { SectionCard } from '../shared/SectionCard';
import { FieldRenderer } from '../shared/FieldRenderer';

/**
 * Price details interface for transportation
 */
interface TransportationPriceDetails {
  display_price?: string;
  one_way_price?: number;
  round_trip_price?: number;
  currency?: string;
  discounts?: string[];
}

/**
 * Props for TransportationPricing component
 */
interface TransportationPricingProps {
  /** Price details for transportation */
  priceDetails: TransportationPriceDetails;
}

/**
 * Component for displaying transportation pricing
 * Shows one-way, round-trip prices, and available discounts
 * 
 * @component
 */
export const TransportationPricing: React.FC<TransportationPricingProps> = ({
  priceDetails
}) => {
  const formatPrice = (price: number | undefined, currency: string = 'USD') => {
    if (!price) return null;
    return `${currency} ${price.toLocaleString()}`;
  };

  return (
    <SectionCard title="Tarifas" icon="💰">
      <FieldRenderer
        label="Precio Mostrado"
        value={priceDetails.display_price}
        type="currency"
        icon="💵"
      />
      <FieldRenderer
        label="Tarifa Solo Ida"
        value={formatPrice(priceDetails.one_way_price, priceDetails.currency)}
        type="currency"
        icon="➡️"
      />
      <FieldRenderer
        label="Tarifa Ida y Vuelta"
        value={formatPrice(priceDetails.round_trip_price, priceDetails.currency)}
        type="currency"
        icon="🔄"
      />
      <FieldRenderer label="Moneda" value={priceDetails.currency} icon="💱" />
      
      {priceDetails.discounts && priceDetails.discounts.length > 0 && (
        <FieldRenderer
          label="Descuentos Disponibles"
          value=""
          type="list"
          listItems={priceDetails.discounts}
          icon="🎟️"
        />
      )}
    </SectionCard>
  );
};
