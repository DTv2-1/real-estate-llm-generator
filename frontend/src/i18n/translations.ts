export type Language = 'es' | 'en';

export interface Translations {
  // Dashboard
  dashboard: {
    title: string;
    subtitle: string;
    dataCollector: string;
    dataCollectorDesc: string;
    properties: string;
    propertiesDesc: string;
    chatbot: string;
    chatbotDesc: string;
    access: string;
    backendStatus: string;
    connected: string;
  };
  
  // Header
  header: {
    logo: string;
    dataCollector: string;
    chatbot: string;
    properties: string;
  };
  
  // Sidebar
  sidebar: {
    savedProperties: string;
    organizedBy: string;
    noProperties: string;
    refresh: string;
    clearAll: string;
  };
  
  // Categories
  categories: {
    newProjects: string;
    housesForSale: string;
    apartmentsForSale: string;
    businessForSale: string;
    lotsLand: string;
    farmsForSale: string;
    housesForRent: string;
    apartmentsForRent: string;
    commercialForRent: string;
    other: string;
  };
  
  // PropertyList
  propertyList: {
    loading: string;
    title: string;
    subtitle: string;
    totalProperties: string;
    withEmbeddings: string;
    indexed: string;
    notIndexed: string;
    priceNotAvailable: string;
    suggestedQueries: string;
    howMuchCost: string;
    tellMeMore: string;
    thePropertyIn: string;
    thisProperty: string;
    chatbotTips: string;
    askLocations: string;
    useFilters: string;
    compareProperties: string;
    askAmenities: string;
    bedrooms: string;
    bathrooms: string;
    propertiesIn: string;
    housesWith: string;
    under: string;
    whatsDifference: string;
    between: string;
    and: string;
    withPool: string;
  };
  
  // DataCollector
  dataCollector: {
    title: string;
    subtitle: string;
    backToSearch: string;
    inputType: string;
    url: string;
    textHtml: string;
    sourceWebsite: string;
    loading: string;
    propertyUrl: string;
    propertyUrlPlaceholder: string;
    propertyText: string;
    propertyTextPlaceholder: string;
    processProperty: string;
    processing: string;
    connectedRealtime: string;
    scrapingFrom: string;
    propertiesProcessedToday: string;
    recentProperties: string;
    mayTake: string;
    extractedData: string;
    confidence: string;
    source: string;
    propertyName: string;
    listingId: string;
    listingStatus: string;
    price: string;
    type: string;
    location: string;
    bedrooms: string;
    bathrooms: string;
    squareMeters: string;
    lotSize: string;
    dateListed: string;
    status: string;
    description: string;
    viewOnMaps: string;
    saveToDatabase: string;
    editDetails: string;
    newProperty: string;
    extractionError: string;
    noPropertiesSaved: string;
    startProcessing: string;
    savedProperties: string;
    organizedBy: string;
    refresh: string;
    clearAllHistory: string;
    quickLinks: string;
    copyIndividualUrls: string;
    fastExtraction: string;
    aiPowered: string;
    duplicateDetected: string;
    alreadyExists: string;
    notSavedAgain: string;
    name: string;
    savedSuccessfully: string;
    propertyId: string;
    errorSaving: string;
    sureDeleteAll: string;
    // Instructions
    howToUse: string;
    step1Title: string;
    step1Desc: string;
    step2Title: string;
    step2Desc: string;
    step3Title: string;
    step3Desc: string;
    step4Title: string;
    step4Desc: string;
    tips: string;
    tip1: string;
    tip2: string;
    tip3: string;
  };
  
  // Chatbot
  chatbot: {
    welcome: string;
    conversations: string;
    newChat: string;
    noConversations: string;
    messages: string;
    sources: string;
    relevance: string;
    placeholder: string;
    changeToSpanish: string;
    changeToEnglish: string;
    newConversation: string;
    tryAsking: string;
    bedrooms: string;
    bathrooms: string;
    exampleBeaches: string;
    exampleBedrooms: string;
    exampleLuxury: string;
    queryBeaches: string;
    queryBedrooms: string;
    queryLuxury: string;
  };
  
  // ErrorBoundary
  error: {
    somethingWrong: string;
    unexpectedError: string;
    reload: string;
  };
  
  // Batch Processing
  batchProcessing: {
    title: string;
    subtitle: string;
    processUrls: string;
    pasteUrls: string;
    urlsPlaceholder: string;
    processButton: string;
    processing: string;
    exportResults: string;
    resultsFound: string;
    noResults: string;
    readyToProcess: string;
    pasteUrlsInstructions: string;
    pressProcess: string;
    automatic: string;
    fast: string;
    accurate: string;
    
    // Left panel - Export options
    resultsHeading: string;
    googleSheets: string;
    googleSheetsDesc: string;
    database: string;
    databaseDesc: string;
    excelFile: string;
    excelFileDesc: string;
    
    // Results section
    resultsProcessing: string;
    total: string;
    
    // Batch items status
    pending: string;
    processing_status: string;
    completed: string;
    error: string;
    
    // Processing messages
    startingProcess: string;
    scrapingPage: string;
    extractingData: string;
    finalizing: string;
    
    // Google Sheets export
    detectingContentTypes: string;
    contentTypesDetected: string;
    automaticTabs: string;
    sheetUrlPlaceholder: string;
    exportToSheets: string;
    exporting: string;
    exportComplete: string;
    exportError: string;
    verifySheetAccess: string;
    noCompleted: string;
    noCompletedSave: string;
    
    // Modal
    propertyDetails: string;
    completeInfo: string;
    extractedData: string;
    sourceUrl: string;
    viewAllDetails: string;
    copyJson: string;
    copied: string;
    
    // Notifications
    exportSuccess: string;
    exportFailed: string;
    errorDetails: string;
  };
  
  // Common
  common: {
    na: string;
    yes: string;
    no: string;
    cancel: string;
    confirm: string;
    save: string;
    edit: string;
    delete: string;
    close: string;
    back: string;
  };
}

export const translations: Record<Language, Translations> = {
  es: {
    dashboard: {
      title: 'Plataforma KP Real Estate',
      subtitle: 'Sistema integral de gestión inmobiliaria con IA',
      dataCollector: 'Colector de Datos',
      dataCollectorDesc: 'Recolección y gestión de propiedades',
      properties: 'Propiedades',
      propertiesDesc: 'Ver propiedades indexadas',
      chatbot: 'Chatbot IA',
      chatbotDesc: 'Asistente virtual inmobiliario',
      access: 'Acceder',
      backendStatus: 'API Backend',
      connected: 'Conectado',
    },
    header: {
      logo: 'LLM Inmobiliario',
      dataCollector: 'Colector de Datos',
      chatbot: 'Chatbot',
      properties: 'Propiedades',
    },
    sidebar: {
      savedProperties: 'Propiedades Guardadas',
      organizedBy: 'Organizadas por categoría',
      noProperties: 'Aún no hay propiedades guardadas',
      refresh: 'Actualizar',
      clearAll: 'Borrar Todo el Historial',
    },
    categories: {
      newProjects: 'Proyectos Nuevos',
      housesForSale: 'Casas en Venta',
      apartmentsForSale: 'Apartamentos en Venta',
      businessForSale: 'Negocios en Venta',
      lotsLand: 'Lotes/Terrenos',
      farmsForSale: 'Fincas en Venta',
      housesForRent: 'Casas en Alquiler',
      apartmentsForRent: 'Apartamentos en Alquiler',
      commercialForRent: 'Locales Comerciales',
      other: 'Otros',
    },
    propertyList: {
      loading: 'Cargando propiedades...',
      title: 'Propiedades Indexadas',
      subtitle: 'Propiedades disponibles para consultas del chatbot',
      totalProperties: 'Total de Propiedades',
      withEmbeddings: 'Con Embeddings',
      indexed: 'Indexada',
      notIndexed: 'No indexada',
      priceNotAvailable: 'Precio no disponible',
      suggestedQueries: 'Consultas sugeridas:',
      howMuchCost: '¿Cuánto cuesta',
      tellMeMore: 'Cuéntame más sobre',
      thePropertyIn: 'la propiedad en',
      thisProperty: 'esta propiedad',
      chatbotTips: 'Consejos para el Chatbot',
      askLocations: 'Pregunta por ubicaciones específicas:',
      useFilters: 'Usa filtros:',
      compareProperties: 'Compara propiedades:',
      askAmenities: 'Pregunta sobre amenidades:',
      bedrooms: 'habitaciones',
      bathrooms: 'baños',
      propertiesIn: '¿Propiedades en',
      housesWith: 'Casas con',
      under: 'bajo',
      whatsDifference: '¿Cuál es la diferencia entre',
      between: 'entre',
      and: 'y',
      withPool: '¿Propiedades con piscina?',
    },
    dataCollector: {
      title: 'Colector de Datos de Propiedades',
      subtitle: 'Pega una URL o texto de propiedad para extraer automáticamente datos estructurados',
      backToSearch: 'Volver a la Búsqueda',
      inputType: 'Tipo de Entrada',
      url: 'URL',
      textHtml: 'Texto/HTML',
      sourceWebsite: 'Sitio Web de Origen',
      loading: 'Cargando...',
      propertyUrl: 'URL de la Propiedad',
      propertyUrlPlaceholder: 'https://encuentra24.com/property/...',
      propertyText: 'Texto/HTML de la Propiedad',
      propertyTextPlaceholder: 'Pega la descripción, HTML o texto de la propiedad aquí...',
      processProperty: 'Procesar Propiedad',
      processing: 'Procesando desde',
      connectedRealtime: 'Conectado en tiempo real',
      scrapingFrom: 'Extrayendo de',
      propertiesProcessedToday: 'Propiedades procesadas hoy',
      recentProperties: 'Últimas Propiedades Agregadas',
      mayTake: 'Esto puede tomar 10-30 segundos',
      extractedData: 'Datos Extraídos de la Propiedad',
      confidence: 'Confianza',
      source: 'Origen:',
      propertyName: 'Nombre de la Propiedad',
      listingId: 'ID de Listado',
      listingStatus: 'Estado del Listado',
      price: 'Precio (USD)',
      type: 'Tipo',
      location: 'Ubicación',
      bedrooms: 'Habitaciones',
      bathrooms: 'Baños',
      squareMeters: 'Metros Cuadrados',
      lotSize: 'Tamaño del Lote (m²)',
      dateListed: 'Fecha de Listado',
      status: 'Estado',
      description: 'Descripción',
      viewOnMaps: 'Ver en Google Maps',
      saveToDatabase: 'Guardar en Base de Datos',
      editDetails: 'Editar Detalles',
      newProperty: 'Nueva Propiedad',
      extractionError: '⚠️ Error de Extracción',
      noPropertiesSaved: 'Aún no hay propiedades guardadas',
      startProcessing: 'Comienza procesando una URL de propiedad',
      savedProperties: 'Propiedades Guardadas',
      organizedBy: 'Organizadas por categoría',
      refresh: 'Actualizar',
      clearAllHistory: 'Borrar Todo el Historial',
      quickLinks: 'Enlaces rápidos',
      copyIndividualUrls: 'Copia URLs de propiedades individuales (no páginas de búsqueda/listado).',
      fastExtraction: 'Extracción rápida (específica del sitio)',
      aiPowered: 'Extracción con IA',
      duplicateDetected: '⚠️ Propiedad Duplicada Detectada',
      alreadyExists: 'Esta propiedad ya existe en la base de datos:',
      notSavedAgain: 'La propiedad NO se guardó nuevamente.',
      name: 'Nombre:',
      savedSuccessfully: '✓ ¡Propiedad guardada exitosamente!',
      propertyId: 'ID de Propiedad:',
      errorSaving: 'Error al guardar la propiedad:',
      sureDeleteAll: '¿Estás seguro de que deseas eliminar todas las propiedades guardadas?',
      // Instructions
      howToUse: '¿Cómo usar el colector?',
      step1Title: '1. Copia el enlace',
      step1Desc: 'Ve al sitio web de bienes raíces y copia la URL completa de la propiedad',
      step2Title: '2. Pega aquí',
      step2Desc: 'Pega el enlace en el campo de "URL de la Propiedad" de abajo',
      step3Title: '3. Procesa',
      step3Desc: 'Haz clic en "Procesar Propiedad" y espera 10-30 segundos',
      step4Title: '4. Revisa y guarda',
      step4Desc: 'Verifica que los datos extraídos sean correctos y guarda en la base de datos',
      tips: '💡 Consejos útiles',
      tip1: 'Usa URLs individuales de propiedades, no páginas de búsqueda',
      tip2: 'Si sale error, verifica que el enlace esté completo y correcto',
      tip3: 'Las propiedades duplicadas no se guardarán automáticamente',
    },
    chatbot: {
      welcome: `¡Hola! Soy tu asistente de Kelly Properties. Puedo ayudarte a encontrar la propiedad perfecta en Costa Rica. ¿Qué estás buscando?

Puedes preguntar sobre:
• Propiedades por ubicación (Tamarindo, Manuel Antonio, etc.)
• Filtros específicos (precio, habitaciones, amenidades)
• Información sobre una propiedad en particular`,
      conversations: 'Conversaciones',
      newChat: 'Nuevo Chat',
      noConversations: 'No hay conversaciones aún',
      messages: 'mensajes',
      sources: 'Fuentes consultadas:',
      relevance: 'relevancia',
      placeholder: 'Escribe tu pregunta aquí...',
      changeToSpanish: 'Cambiar a Español',
      changeToEnglish: 'Switch to English',
      newConversation: 'Nueva conversación',
      tryAsking: 'Intenta preguntar:',
      bedrooms: 'habitaciones',
      bathrooms: 'baños',
      exampleBeaches: 'Playas',
      exampleBedrooms: '3 habitaciones',
      exampleLuxury: 'Lujo',
      queryBeaches: '¿Propiedades en Tamarindo?',
      queryBedrooms: 'Casas con 3 habitaciones bajo $300K',
      queryLuxury: '¿Propiedades de lujo con piscina?',
    },
    batchProcessing: {
      title: 'Procesamiento en Lotes',
      subtitle: 'Procesa múltiples URLs de propiedades simultáneamente',
      processUrls: 'Procesar URLs en Lote',
      pasteUrls: 'Pega las URLs aquí',
      urlsPlaceholder: 'Ingresa URLs separadas por saltos de línea o comas. Ejemplo:\nhttps://ejemplo.com/propiedad1\nhttps://ejemplo.com/propiedad2\nhttps://ejemplo.com/propiedad3',
      processButton: 'PROCESAR',
      processing: 'Procesando...',
      exportResults: 'Exportar Resultados',
      resultsFound: 'Resultados encontrados',
      noResults: 'Sin resultados',
      readyToProcess: 'Listo para procesar',
      pasteUrlsInstructions: 'Pega las URLs de las propiedades en el panel izquierdo y presiona',
      pressProcess: 'PROCESAR',
      automatic: 'Automático',
      fast: 'Rápido',
      accurate: 'Preciso',
      
      // Left panel - Export options
      resultsHeading: 'Resultados del Procesamiento',
      googleSheets: 'Google Sheets',
      googleSheetsDesc: 'Exporta automáticamente a una hoja de cálculo en la nube',
      database: 'Base de Datos',
      databaseDesc: 'Guarda permanentemente en PostgreSQL',
      excelFile: 'Archivo Excel',
      excelFileDesc: 'Descarga un archivo .xlsx local',
      
      // Results section
      resultsProcessing: 'Resultados del Procesamiento',
      total: 'total',
      
      // Batch items status
      pending: 'Pendiente',
      processing_status: 'Procesando',
      completed: 'Completado',
      error: 'Error',
      
      // Processing messages
      startingProcess: 'Iniciando proceso...',
      scrapingPage: 'Scrapeando página...',
      extractingData: 'Extrayendo datos...',
      finalizing: 'Finalizando...',
      
      // Google Sheets export
      detectingContentTypes: 'Tipos de contenido detectados:',
      contentTypesDetected: '📊 Tipos de contenido detectados:',
      automaticTabs: '💡 Se crearán tabs automáticos "Específicos" y "Generales" según el tipo de página',
      sheetUrlPlaceholder: 'URL de Google Sheet para',
      exportToSheets: 'Exportar a',
      exporting: 'Exportando...',
      exportComplete: 'Exportación Completa',
      exportError: 'Error de Exportación',
      verifySheetAccess: 'Verifica que los sheets estén compartidos correctamente con la cuenta de servicio de Google',
      noCompleted: 'No hay resultados completados aún',
      noCompletedSave: 'No hay resultados completados para guardar',
      
      // Modal
      propertyDetails: 'Detalles de Propiedad',
      completeInfo: 'Información completa extraída',
      extractedData: 'Datos Extraídos de la Propiedad',
      sourceUrl: 'URL DE ORIGEN',
      viewAllDetails: 'Click para ver todos los detalles',
      copyJson: 'Copiar JSON',
      copied: '✓ Copiado',
      
      // Notifications
      exportSuccess: 'Los datos fueron exportados exitosamente',
      exportFailed: 'Fallo la exportación de los datos',
      errorDetails: 'Detalles del error:',
    },
    error: {
      somethingWrong: 'Algo salió mal',
      unexpectedError: 'Ocurrió un error inesperado',
      reload: 'Recargar Página',
    },
    common: {
      na: 'N/A',
      yes: 'Sí',
      no: 'No',
      cancel: 'Cancelar',
      confirm: 'Confirmar',
      save: 'Guardar',
      edit: 'Editar',
      delete: 'Eliminar',
      close: 'Cerrar',
      back: 'Volver',
    },
  },
  en: {
    dashboard: {
      title: 'KP Real Estate Platform',
      subtitle: 'Comprehensive AI-powered real estate management system',
      dataCollector: 'Data Collector',
      dataCollectorDesc: 'Property collection and management',
      properties: 'Properties',
      propertiesDesc: 'View indexed properties',
      chatbot: 'AI Chatbot',
      chatbotDesc: 'Virtual real estate assistant',
      access: 'Access',
      backendStatus: 'Backend API',
      connected: 'Connected',
    },
    header: {
      logo: 'Real Estate LLM',
      dataCollector: 'Data Collector',
      chatbot: 'Chatbot',
      properties: 'Properties',
    },
    sidebar: {
      savedProperties: 'Saved Properties',
      organizedBy: 'Organized by category',
      noProperties: 'No properties saved yet',
      refresh: 'Refresh',
      clearAll: 'Clear All History',
    },
    categories: {
      newProjects: 'New Projects',
      housesForSale: 'Houses for Sale',
      apartmentsForSale: 'Apartments for Sale',
      businessForSale: 'Businesses for Sale',
      lotsLand: 'Lots/Land',
      farmsForSale: 'Farms for Sale',
      housesForRent: 'Houses for Rent',
      apartmentsForRent: 'Apartments for Rent',
      commercialForRent: 'Commercial for Rent',
      other: 'Other',
    },
    propertyList: {
      loading: 'Loading properties...',
      title: 'Indexed Properties',
      subtitle: 'Properties available for chatbot queries',
      totalProperties: 'Total Properties',
      withEmbeddings: 'With Embeddings',
      indexed: 'Indexed',
      notIndexed: 'Not indexed',
      priceNotAvailable: 'Price not available',
      suggestedQueries: 'Suggested queries:',
      howMuchCost: 'How much does',
      tellMeMore: 'Tell me more about',
      thePropertyIn: 'the property in',
      thisProperty: 'this property',
      chatbotTips: 'Chatbot Tips',
      askLocations: 'Ask for specific locations:',
      useFilters: 'Use filters:',
      compareProperties: 'Compare properties:',
      askAmenities: 'Ask about amenities:',
      bedrooms: 'bedrooms',
      bathrooms: 'bathrooms',
      propertiesIn: 'Properties in',
      housesWith: 'Houses with',
      under: 'under',
      whatsDifference: "What's the difference between",
      between: 'between',
      and: 'and',
      withPool: 'Properties with pool?',
    },
    dataCollector: {
      title: 'Property Data Collector',
      subtitle: 'Paste a property URL or text to automatically extract structured data',
      backToSearch: 'Back to Search',
      inputType: 'Input Type',
      url: 'URL',
      textHtml: 'Text/HTML',
      sourceWebsite: 'Source Website',
      loading: 'Loading...',
      propertyUrl: 'Property URL',
      propertyUrlPlaceholder: 'https://encuentra24.com/property/...',
      propertyText: 'Property Text/HTML',
      propertyTextPlaceholder: 'Paste property description, HTML, or text here...',
      processProperty: 'Process Property',
      processing: 'Processing from',
      connectedRealtime: 'Connected in real-time',
      scrapingFrom: 'Extracting from',
      propertiesProcessedToday: 'Properties processed today',
      recentProperties: 'Recently Added Properties',
      mayTake: 'This may take 10-30 seconds',
      extractedData: 'Extracted Property Data',
      confidence: 'Confidence',
      source: 'Source:',
      propertyName: 'Property Name',
      listingId: 'Listing ID',
      listingStatus: 'Listing Status',
      price: 'Price (USD)',
      type: 'Type',
      location: 'Location',
      bedrooms: 'Bedrooms',
      bathrooms: 'Bathrooms',
      squareMeters: 'Square Meters',
      lotSize: 'Lot Size (m²)',
      dateListed: 'Date Listed',
      status: 'Status',
      description: 'Description',
      viewOnMaps: 'View on Google Maps',
      saveToDatabase: 'Save to Database',
      editDetails: 'Edit Details',
      newProperty: 'New Property',
      extractionError: '⚠️ Extraction Error',
      noPropertiesSaved: 'No properties saved yet',
      startProcessing: 'Start by processing a property URL',
      savedProperties: 'Saved Properties',
      organizedBy: 'Organized by category',
      refresh: 'Refresh',
      clearAllHistory: 'Clear All History',
      quickLinks: 'Quick links',
      copyIndividualUrls: 'Copy individual property URLs (not search/listing pages).',
      fastExtraction: 'Fast extraction (site-specific)',
      aiPowered: 'AI-powered extraction',
      duplicateDetected: '⚠️ Duplicate Property Detected',
      alreadyExists: 'This property already exists in the database:',
      notSavedAgain: 'The property was NOT saved again.',
      name: 'Name:',
      savedSuccessfully: '✓ Property saved successfully!',
      propertyId: 'Property ID:',
      errorSaving: 'Error saving property:',
      sureDeleteAll: 'Are you sure you want to delete all saved properties?',
      // Instructions
      howToUse: 'How to use the collector?',
      step1Title: '1. Copy the link',
      step1Desc: 'Go to the real estate website and copy the full property URL',
      step2Title: '2. Paste here',
      step2Desc: 'Paste the link in the "Property URL" field below',
      step3Title: '3. Process',
      step3Desc: 'Click "Process Property" and wait 10-30 seconds',
      step4Title: '4. Review and save',
      step4Desc: 'Verify the extracted data is correct and save to database',
      tips: '💡 Useful tips',
      tip1: 'Use individual property URLs, not search pages',
      tip2: 'If you get an error, verify the link is complete and correct',
      tip3: 'Duplicate properties will not be saved automatically',
    },
    chatbot: {
      welcome: `Hello! I'm your Kelly Properties assistant. I can help you find the perfect property in Costa Rica. What are you looking for?

You can ask about:
• Properties by location (Tamarindo, Manuel Antonio, etc.)
• Specific filters (price, bedrooms, amenities)
• Information about a particular property`,
      conversations: 'Conversations',
      newChat: 'New Chat',
      noConversations: 'No conversations yet',
      messages: 'messages',
      sources: 'Sources consulted:',
      relevance: 'relevance',
      placeholder: 'Type your question here...',
      changeToSpanish: 'Cambiar a Español',
      changeToEnglish: 'Switch to English',
      newConversation: 'New conversation',
      tryAsking: 'Try asking:',
      bedrooms: 'bedrooms',
      bathrooms: 'bathrooms',
      exampleBeaches: 'Beaches',
      exampleBedrooms: '3 bedrooms',
      exampleLuxury: 'Luxury',
      queryBeaches: 'Properties in Tamarindo?',
      queryBedrooms: 'Houses with 3 bedrooms under $300K',
      queryLuxury: 'Luxury properties with pool?',
    },
    batchProcessing: {
      title: 'Batch Processing',
      subtitle: 'Process multiple property URLs simultaneously',
      processUrls: 'Process URLs in Batch',
      pasteUrls: 'Paste URLs here',
      urlsPlaceholder: 'Enter URLs separated by line breaks or commas. Example:\nhttps://example.com/property1\nhttps://example.com/property2\nhttps://example.com/property3',
      processButton: 'PROCESS',
      processing: 'Processing...',
      exportResults: 'Export Results',
      resultsFound: 'Results found',
      noResults: 'No results',
      readyToProcess: 'Ready to process',
      pasteUrlsInstructions: 'Paste property URLs in the left panel and press',
      pressProcess: 'PROCESS',
      automatic: 'Automatic',
      fast: 'Fast',
      accurate: 'Accurate',
      
      // Left panel - Export options
      resultsHeading: 'Processing Results',
      googleSheets: 'Google Sheets',
      googleSheetsDesc: 'Automatically export to a cloud spreadsheet',
      database: 'Database',
      databaseDesc: 'Permanently save to PostgreSQL',
      excelFile: 'Excel File',
      excelFileDesc: 'Download a local .xlsx file',
      
      // Results section
      resultsProcessing: 'Processing Results',
      total: 'total',
      
      // Batch items status
      pending: 'Pending',
      processing_status: 'Processing',
      completed: 'Completed',
      error: 'Error',
      
      // Processing messages
      startingProcess: 'Starting process...',
      scrapingPage: 'Scraping page...',
      extractingData: 'Extracting data...',
      finalizing: 'Finalizing...',
      
      // Google Sheets export
      detectingContentTypes: 'Content types detected:',
      contentTypesDetected: '📊 Content types detected:',
      automaticTabs: '💡 Automatic "Specific" and "General" tabs will be created based on the page type',
      sheetUrlPlaceholder: 'Google Sheet URL for',
      exportToSheets: 'Export to',
      exporting: 'Exporting...',
      exportComplete: 'Export Complete',
      exportError: 'Export Error',
      verifySheetAccess: 'Verify that the sheets are correctly shared with the Google service account',
      noCompleted: 'No completed results yet',
      noCompletedSave: 'No completed results to save',
      
      // Modal
      propertyDetails: 'Property Details',
      completeInfo: 'Complete extracted information',
      extractedData: 'Extracted Property Data',
      sourceUrl: 'SOURCE URL',
      viewAllDetails: 'Click to see all details',
      copyJson: 'Copy JSON',
      copied: '✓ Copied',
      
      // Notifications
      exportSuccess: 'Data was successfully exported',
      exportFailed: 'Data export failed',
      errorDetails: 'Error details:',
    },
    error: {
      somethingWrong: 'Something went wrong',
      unexpectedError: 'An unexpected error occurred',
      reload: 'Reload Page',
    },
    common: {
      na: 'N/A',
      yes: 'Yes',
      no: 'No',
      cancel: 'Cancel',
      confirm: 'Confirm',
      save: 'Save',
      edit: 'Edit',
      delete: 'Delete',
      close: 'Close',
      back: 'Back',
    },
  },
};

export function getTranslation(lang: Language): Translations {
  return translations[lang];
}
