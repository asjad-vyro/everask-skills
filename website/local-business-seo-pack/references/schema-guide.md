# Schema guide

## Subtypes of LocalBusiness
Plumber, Electrician, RoofingContractor, HVACBusiness, AutoRepair, BeautySalon, HairSalon, Dentist, Physician, LegalService, AccountingService, RealEstateAgent, Restaurant, CafeOrCoffeeShop, BarOrPub, Bakery, Hotel, Store, ProfessionalService. Use `LocalBusiness` if none fits.

## LocalBusiness properties
Required: `@type`, `name`, `@id` (`{url}/#organization`), `url`, `telephone` (international, e.g. `+44-113-496-0000`), `address`.
Include when the user gave it: `image`, `description`, `email`, `priceRange` (`$` to `$$$$`, or text the user gave), `geo`, `openingHoursSpecification`, `areaServed`, `sameAs`, `logo`, `foundingDate`, `paymentAccepted`, `taxID` (any local tax or company number the user gave).

PostalAddress: `streetAddress`, `addressLocality`, `addressRegion`, `postalCode`, `addressCountry` (2-letter ISO code).

Phone: schema value international; the visible link is `tel:+441134960000`.

## Example (made-up values, for shape only)
```json
{
  "@context": "https://schema.org",
  "@type": "Plumber",
  "@id": "https://www.example.com/#organization",
  "name": "Example Plumbing",
  "url": "https://www.example.com",
  "telephone": "+44-113-496-0000",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "1 High Street",
    "addressLocality": "Leeds",
    "postalCode": "LS1 1AA",
    "addressCountry": "GB"
  },
  "openingHoursSpecification": [
    {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "08:00", "closes": "17:00"},
    {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Saturday"], "opens": "09:00", "closes": "12:00"}
  ],
  "areaServed": [{"@type": "City", "name": "Leeds"}],
  "sameAs": ["https://www.facebook.com/example"]
}
```
Opening hours use 24-hour `HH:MM`. A business open past midnight: `closes` "02:00" is allowed.

## Service
```json
{"@context": "https://schema.org", "@type": "Service", "name": "Boiler repair", "description": "...", "provider": {"@id": "https://www.example.com/#organization"}, "areaServed": {"@type": "City", "name": "Leeds"}, "serviceType": "Plumbing"}
```

## FAQPage
```json
{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "...", "acceptedAnswer": {"@type": "Answer", "text": "..."}}]}
```

## Common errors
Missing `@context`; telephone not international; missing `@id`; empty `areaServed`; trailing commas.
