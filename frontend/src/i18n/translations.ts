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
    welcomeSubtitle: string;
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

  // BatchProcessing
  batchProcessing: {
    title: string;
    subtitle: string;
    urlList: string;
    urlsLabel: string;
    urlsPlaceholder: string;
    process: string;
    stop: string;
    processing: string;
    processingOf: string;
    clear: string;
    clearTooltip: string;
    statistics: string;
    total: string;
    completed: string;
    errors: string;
    exportResults: string;
    googleSheets: string;
    exportToSheets: string;
    database: string;
    saveToDatabase: string;
    excelFile: string;
    downloadExcel: string;
    exportNow: string;
    savesPermanently: string;
    downloadLocal: string;
    exportsToCloud: string;
    resultsProcessing: string;
    enterSheetLink: string;
    noCompletedResults: string;
    noResultsToExport: string;
    noResultsToSave: string;
    noResultsToDownload: string;
    propertiesExported: string;
    propertiesSaved: string;
    propertiesDownloaded: string;
    errorExporting: string;
    errorSaving: string;
    errorDownloading: string;
    verifySheetShared: string;
    enterAtLeastOneUrl: string;
    maxUrlsPerBatch: string;
    readyToProcess: string;
    pasteUrlsAndProcess: string;
    automatic: string;
    fast: string;
    precise: string;
  };

  // GoogleSheets
  googleSheets: {
    title: string;
    subtitle: string;
    createNewTemplate: string;
    createTemplateDesc: string;
    sheetTitle: string;
    sheetTitlePlaceholder: string;
    createTemplate: string;
    creating: string;
    templateCreated: string;
    spreadsheetId: string;
    openGoogleSheet: string;
    nextSteps: string;
    step1OpenSheet: string;
    step2ShareSheet: string;
    step3PasteUrls: string;
    step4WritePending: string;
    step5ProcessBelow: string;
    processExistingSheet: string;
    processExistingDesc: string;
    sheetIdOrUrl: string;
    sheetIdPlaceholder: string;
    canPasteIdOrUrl: string;
    emailNotification: string;
    emailPlaceholder: string;
    receiveEmailWhenDone: string;
    useResultsSheet: string;
    useResultsSheetDesc: string;
    resultsSheetId: string;
    requiredSteps: string;
    createNewSheet: string;
    shareWithAccount: string;
    giveEditorPermissions: string;
    copyIdHere: string;
    processSheet: string;
    processing: string;
    whatHappens: string;
    readsAllPending: string;
    processesAutomatic: string;
    updatesRealtime: string;
    sendsEmail: string;
    openThisSheet: string;
    resultsSheetCreated: string;
    sheetTitleLabel: string;
    viewResultsInSheets: string;
    functionBlocked: string;
    requiresWorkspace: string;
    blockedMessage: string;
    useFreeAlternative: string;
    freeAlternativeDesc: string;
    quickGuide: string;
    guideStep1: string;
    guideStep2: string;
    guideStep3: string;
    guideStep4: string;
    createManualSheet: string;
    howItWorks: string;
    step1Create: string;
    step1CreateDesc: string;
    step2AddUrls: string;
    step2AddUrlsDesc: string;
    step3Process: string;
    step3ProcessDesc: string;
    enterTemplateTitle: string;
    enterSheetId: string;
    enterValidEmail: string;
    enterResultsSheetId: string;
    templateCreatedSuccess: string;
    errorCreatingTemplate: string;
    networkError: string;
    errorProcessingSheet: string;
    completedProcessed: string;
    resultsSheetCreatedMsg: string;
  };

  // Tutorial
  tutorial: {
    chooseWebsite: string;
    step1Title: string;
    step1Subtitle: string;
    step1Point1: string;
    step1Point2: string;
    step1Point3: string;
    example: string;
    next: string;
    skip: string;
    pasteHere: string;
    step2Title: string;
    step2Subtitle: string;
    clickHere: string;
    step3Title: string;
    step3Subtitle: string;
    step3Point1: string;
    step3Point2: string;
    step3Point3: string;
    step4Title: string;
    step4Subtitle: string;
    step4Point1Title: string;
    step4Point1Desc: string;
    step4Point2Title: string;
    step4Point2Desc: string;
    step4Point3Title: string;
    step4Point3Desc: string;
    understood: string;
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
      welcomeSubtitle: 'Puedo ayudarte a analizar propiedades, comparar precios y gestionar datos inmobiliarios.',
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
    batchProcessing: {
      title: 'Procesamiento en Lote',
      subtitle: 'Extrae datos de múltiples propiedades automáticamente',
      urlList: 'Lista de URLs',
      urlsLabel: 'URLs de Propiedades',
      urlsPlaceholder: 'https://encuentra24.com/property/...\nhttps://brevitas.com/property/...\nhttps://coldwellbankercostarica.com/...',
      process: 'PROCESAR',
      stop: 'DETENER',
      processing: 'Procesando...',
      processingOf: 'de',
      clear: 'Limpiar todo',
      clearTooltip: 'Limpiar todo',
      statistics: 'Estadísticas',
      total: 'Total',
      completed: 'Completadas',
      errors: 'Errores',
      exportResults: 'Exportar Resultados',
      googleSheets: 'Google Sheets',
      exportToSheets: 'Exporta automáticamente a una hoja de cálculo en la nube',
      database: 'Base de Datos',
      saveToDatabase: 'Guarda permanentemente en PostgreSQL',
      excelFile: 'Archivo Excel',
      downloadExcel: 'Descarga un archivo .xlsx local',
      exportNow: 'Exportar Ahora',
      savesPermanently: 'Guarda permanentemente en PostgreSQL',
      downloadLocal: 'Descarga un archivo .csv local',
      exportsToCloud: 'Exporta automáticamente a una hoja de cálculo en la nube',
      resultsProcessing: 'Resultados del Procesamiento',
      enterSheetLink: 'Por favor ingresa el link del Google Sheet',
      noCompletedResults: 'No hay resultados completados',
      noResultsToExport: 'No hay resultados completados para exportar',
      noResultsToSave: 'No hay resultados completados para guardar',
      noResultsToDownload: 'No hay resultados completados para descargar',
      propertiesExported: 'propiedades exportadas exitosamente a Google Sheets',
      propertiesSaved: 'propiedades guardadas exitosamente en la base de datos',
      propertiesDownloaded: 'propiedades descargadas en formato CSV',
      errorExporting: 'Error al exportar a Google Sheets',
      errorSaving: 'Error al guardar en la base de datos',
      errorDownloading: 'Error al descargar el archivo',
      verifySheetShared: 'Verifica que el sheet esté compartido correctamente.',
      enterAtLeastOneUrl: 'Por favor ingresa al menos una URL',
      maxUrlsPerBatch: 'Máximo 50 URLs por lote',
      readyToProcess: 'Listo para procesar',
      pasteUrlsAndProcess: 'Pega las URLs de las propiedades en el panel izquierdo y presiona PROCESAR para comenzar',
      automatic: 'Automático',
      fast: 'Rápido',
      precise: 'Preciso',
    },
    googleSheets: {
      title: 'Integración con Google Sheets',
      subtitle: 'Gestiona múltiples propiedades desde Google Sheets',
      createNewTemplate: 'Crear Nuevo Template',
      createTemplateDesc: 'Crea un nuevo Google Sheet con las columnas configuradas automáticamente',
      sheetTitle: 'Título del Sheet',
      sheetTitlePlaceholder: 'Propiedades Enero 2026',
      createTemplate: 'CREAR TEMPLATE',
      creating: 'CREANDO...',
      templateCreated: 'Template Creado',
      spreadsheetId: 'Spreadsheet ID:',
      openGoogleSheet: 'Abrir Google Sheet',
      nextSteps: '📋 Próximos pasos:',
      step1OpenSheet: 'Abre el link del Google Sheet',
      step2ShareSheet: 'Compártelo con la cuenta de servicio',
      step3PasteUrls: 'Pega las URLs en la columna A',
      step4WritePending: 'Escribe "Pendiente" en la columna C',
      step5ProcessBelow: 'Procesa usando la sección de abajo →',
      processExistingSheet: 'Procesar Sheet Existente',
      processExistingDesc: 'Procesa todas las URLs con status "Pendiente" de un Google Sheet',
      sheetIdOrUrl: 'Google Sheet ID o URL',
      sheetIdPlaceholder: '1abc123xyz o https://docs.google.com/spreadsheets/d/...',
      canPasteIdOrUrl: 'Puedes pegar el ID o la URL completa del sheet',
      emailNotification: 'Email para notificación',
      emailPlaceholder: 'asistente@example.com',
      receiveEmailWhenDone: 'Recibirás un email cuando el procesamiento termine',
      useResultsSheet: '📊 Usar Google Sheet de Resultados',
      useResultsSheetDesc: 'Escribe los resultados en un Google Sheet separado para fácil revisión y análisis. Crea el sheet manualmente y compártelo con la service account primero.',
      resultsSheetId: '📋 Google Sheet ID de Resultados',
      requiredSteps: '⚠️ Pasos requeridos:',
      createNewSheet: 'Crea un Google Sheet nuevo con headers (ver documentación)',
      shareWithAccount: 'Comparte con:',
      giveEditorPermissions: 'Dale permisos de Editor',
      copyIdHere: 'Copia el ID del sheet aquí',
      processSheet: 'PROCESAR SHEET',
      processing: 'PROCESANDO...',
      whatHappens: '⚡ Qué sucede:',
      readsAllPending: 'Lee todas las filas con "Pendiente"',
      processesAutomatic: 'Procesa cada URL automáticamente',
      updatesRealtime: 'Actualiza el status en tiempo real',
      sendsEmail: 'Envía email con resultados al terminar',
      openThisSheet: 'Abrir este Sheet en Google',
      resultsSheetCreated: 'Google Sheet de Resultados Creado',
      sheetTitleLabel: 'Título:',
      viewResultsInSheets: 'Ver Resultados en Google Sheets',
      functionBlocked: 'Función Bloqueada',
      requiresWorkspace: 'REQUIERE GOOGLE WORKSPACE',
      blockedMessage: 'La creación automática de Google Sheets solo funciona con cuentas de Google Workspace (servicio de pago).',
      useFreeAlternative: 'Usa la Alternativa Gratuita',
      freeAlternativeDesc: 'Crea tu sheet en sheets.google.com y procésalo con Sección 2',
      quickGuide: 'Guía Rápida:',
      guideStep1: 'Nuevo sheet → Headers: URL|Status|etc',
      guideStep2: 'URLs en columna A → "Pendiente" en C',
      guideStep3: 'Compartir con service account',
      guideStep4: '¡Usar Sección 2!',
      createManualSheet: 'Crear Sheet Manual (Gratis)',
      howItWorks: '¿Cómo funciona?',
      step1Create: '1. Crear Template',
      step1CreateDesc: 'Crea un Google Sheet con las columnas ya configuradas. Solo necesitas el título.',
      step2AddUrls: '2. Agregar URLs',
      step2AddUrlsDesc: 'Abre el sheet, pega URLs en columna A y escribe "Pendiente" en columna C.',
      step3Process: '3. Procesar',
      step3ProcessDesc: 'Pega el ID del sheet, tu email, y presiona procesar. Recibirás email cuando termine.',
      enterTemplateTitle: 'Por favor ingresa un título para el template',
      enterSheetId: 'Por favor ingresa el ID del Google Sheet',
      enterValidEmail: 'Por favor ingresa un email válido',
      enterResultsSheetId: 'Por favor ingresa el ID del Google Sheet de resultados o desactiva la opción',
      templateCreatedSuccess: '¡Template creado! Abre el link, compártelo con la cuenta de servicio, y pega tus URLs.',
      errorCreatingTemplate: 'Error al crear template',
      networkError: 'Error de red:',
      errorProcessingSheet: 'Error al procesar sheet',
      completedProcessed: '✅ Completado! Procesadas:',
      resultsSheetCreatedMsg: 'Se creó un Google Sheet con los resultados.',
    },
    tutorial: {
      chooseWebsite: 'ELIGE UN SITIO WEB',
      step1Title: 'Copia el enlace de la propiedad',
      step1Subtitle: 'Desde Encuentra24, Brevitas o Coldwell Banker',
      step1Point1: '1. Abre Encuentra24, Brevitas o Coldwell Banker',
      step1Point2: '2. Busca una propiedad que te interese',
      step1Point3: '3. Copia la URL completa desde el navegador',
      example: 'Ejemplo:',
      next: 'Siguiente',
      skip: 'Saltar',
      pasteHere: '¡PEGA AQUÍ EL ENLACE!',
      step2Title: 'Pega el enlace',
      step2Subtitle: 'Ctrl+V o Cmd+V en el campo resaltado',
      clickHere: '¡HAZ CLIC AQUÍ!',
      step3Title: 'Procesa la propiedad',
      step3Subtitle: 'Haz clic en el botón resaltado',
      step3Point1: 'El proceso toma 10-30 segundos',
      step3Point2: 'Verás una barra de progreso en tiempo real',
      step3Point3: 'Se extraerán automáticamente todos los datos',
      step4Title: 'Revisa y guarda los datos',
      step4Subtitle: 'Verifica que los datos extraídos sean correctos antes de guardar',
      step4Point1Title: 'Verifica los datos',
      step4Point1Desc: 'Precio, ubicación, habitaciones, baños, etc.',
      step4Point2Title: 'Haz clic en "Guardar"',
      step4Point2Desc: 'Si todo se ve bien, guarda la propiedad en la base de datos',
      step4Point3Title: '¡Listo para la siguiente!',
      step4Point3Desc: 'Repite el proceso con otra propiedad',
      understood: '¡Entendido! Comenzar a usar',
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
      welcomeSubtitle: 'I can help you analyze properties, compare prices, and manage real estate data.',
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
    batchProcessing: {
      title: 'Batch Processing',
      subtitle: 'Automatically extract data from multiple properties',
      urlList: 'URL List',
      urlsLabel: 'Property URLs',
      urlsPlaceholder: 'https://encuentra24.com/property/...\nhttps://brevitas.com/property/...\nhttps://coldwellbankercostarica.com/...',
      process: 'PROCESS',
      stop: 'STOP',
      processing: 'Processing...',
      processingOf: 'of',
      clear: 'Clear all',
      clearTooltip: 'Clear all',
      statistics: 'Statistics',
      total: 'Total',
      completed: 'Completed',
      errors: 'Errors',
      exportResults: 'Export Results',
      googleSheets: 'Google Sheets',
      exportToSheets: 'Automatically export to a cloud spreadsheet',
      database: 'Database',
      saveToDatabase: 'Save permanently to PostgreSQL',
      excelFile: 'Excel File',
      downloadExcel: 'Download a local .xlsx file',
      exportNow: 'Export Now',
      savesPermanently: 'Save permanently to PostgreSQL',
      downloadLocal: 'Download a local .csv file',
      exportsToCloud: 'Automatically export to a cloud spreadsheet',
      resultsProcessing: 'Processing Results',
      enterSheetLink: 'Please enter the Google Sheet link',
      noCompletedResults: 'No completed results',
      noResultsToExport: 'No completed results to export',
      noResultsToSave: 'No completed results to save',
      noResultsToDownload: 'No completed results to download',
      propertiesExported: 'properties successfully exported to Google Sheets',
      propertiesSaved: 'properties successfully saved to database',
      propertiesDownloaded: 'properties downloaded in CSV format',
      errorExporting: 'Error exporting to Google Sheets',
      errorSaving: 'Error saving to database',
      errorDownloading: 'Error downloading file',
      verifySheetShared: 'Verify the sheet is shared correctly.',
      enterAtLeastOneUrl: 'Please enter at least one URL',
      maxUrlsPerBatch: 'Maximum 50 URLs per batch',
      readyToProcess: 'Ready to process',
      pasteUrlsAndProcess: 'Paste property URLs in the left panel and press PROCESS to begin',
      automatic: 'Automatic',
      fast: 'Fast',
      precise: 'Precise',
    },
    googleSheets: {
      title: 'Google Sheets Integration',
      subtitle: 'Manage multiple properties from Google Sheets',
      createNewTemplate: 'Create New Template',
      createTemplateDesc: 'Create a new Google Sheet with columns automatically configured',
      sheetTitle: 'Sheet Title',
      sheetTitlePlaceholder: 'Properties January 2026',
      createTemplate: 'CREATE TEMPLATE',
      creating: 'CREATING...',
      templateCreated: 'Template Created',
      spreadsheetId: 'Spreadsheet ID:',
      openGoogleSheet: 'Open Google Sheet',
      nextSteps: '📋 Next steps:',
      step1OpenSheet: 'Open the Google Sheet link',
      step2ShareSheet: 'Share it with the service account',
      step3PasteUrls: 'Paste URLs in column A',
      step4WritePending: 'Write "Pending" in column C',
      step5ProcessBelow: 'Process using the section below →',
      processExistingSheet: 'Process Existing Sheet',
      processExistingDesc: 'Process all URLs with "Pending" status from a Google Sheet',
      sheetIdOrUrl: 'Google Sheet ID or URL',
      sheetIdPlaceholder: '1abc123xyz or https://docs.google.com/spreadsheets/d/...',
      canPasteIdOrUrl: 'You can paste the ID or the complete sheet URL',
      emailNotification: 'Email notification',
      emailPlaceholder: 'assistant@example.com',
      receiveEmailWhenDone: 'You will receive an email when processing is complete',
      useResultsSheet: '📊 Use Results Google Sheet',
      useResultsSheetDesc: 'Write results to a separate Google Sheet for easy review and analysis. Create the sheet manually and share it with the service account first.',
      resultsSheetId: '📋 Results Google Sheet ID',
      requiredSteps: '⚠️ Required steps:',
      createNewSheet: 'Create a new Google Sheet with headers (see documentation)',
      shareWithAccount: 'Share with:',
      giveEditorPermissions: 'Give Editor permissions',
      copyIdHere: 'Copy the sheet ID here',
      processSheet: 'PROCESS SHEET',
      processing: 'PROCESSING...',
      whatHappens: '⚡ What happens:',
      readsAllPending: 'Reads all rows with "Pending"',
      processesAutomatic: 'Processes each URL automatically',
      updatesRealtime: 'Updates status in real-time',
      sendsEmail: 'Sends email with results when done',
      openThisSheet: 'Open this Sheet in Google',
      resultsSheetCreated: 'Results Google Sheet Created',
      sheetTitleLabel: 'Title:',
      viewResultsInSheets: 'View Results in Google Sheets',
      functionBlocked: 'Function Blocked',
      requiresWorkspace: 'REQUIRES GOOGLE WORKSPACE',
      blockedMessage: 'Automatic creation of Google Sheets only works with Google Workspace accounts (paid service).',
      useFreeAlternative: 'Use the Free Alternative',
      freeAlternativeDesc: 'Create your sheet at sheets.google.com and process it with Section 2',
      quickGuide: 'Quick Guide:',
      guideStep1: 'New sheet → Headers: URL|Status|etc',
      guideStep2: 'URLs in column A → "Pending" in C',
      guideStep3: 'Share with service account',
      guideStep4: 'Use Section 2!',
      createManualSheet: 'Create Manual Sheet (Free)',
      howItWorks: 'How does it work?',
      step1Create: '1. Create Template',
      step1CreateDesc: 'Create a Google Sheet with columns already configured. You only need the title.',
      step2AddUrls: '2. Add URLs',
      step2AddUrlsDesc: 'Open the sheet, paste URLs in column A and write "Pending" in column C.',
      step3Process: '3. Process',
      step3ProcessDesc: 'Paste the sheet ID, your email, and press process. You will receive email when done.',
      enterTemplateTitle: 'Please enter a title for the template',
      enterSheetId: 'Please enter the Google Sheet ID',
      enterValidEmail: 'Please enter a valid email',
      enterResultsSheetId: 'Please enter the results Google Sheet ID or disable the option',
      templateCreatedSuccess: 'Template created! Open the link, share it with the service account, and paste your URLs.',
      errorCreatingTemplate: 'Error creating template',
      networkError: 'Network error:',
      errorProcessingSheet: 'Error processing sheet',
      completedProcessed: '✅ Completed! Processed:',
      resultsSheetCreatedMsg: 'A Google Sheet with the results was created.',
    },
    tutorial: {
      chooseWebsite: 'CHOOSE A WEBSITE',
      step1Title: 'Copy the property link',
      step1Subtitle: 'From Encuentra24, Brevitas or Coldwell Banker',
      step1Point1: '1. Open Encuentra24, Brevitas or Coldwell Banker',
      step1Point2: '2. Find a property you\'re interested in',
      step1Point3: '3. Copy the full URL from the browser',
      example: 'Example:',
      next: 'Next',
      skip: 'Skip',
      pasteHere: 'PASTE THE LINK HERE!',
      step2Title: 'Paste the link',
      step2Subtitle: 'Ctrl+V or Cmd+V in the highlighted field',
      clickHere: 'CLICK HERE!',
      step3Title: 'Process the property',
      step3Subtitle: 'Click on the highlighted button',
      step3Point1: 'The process takes 10-30 seconds',
      step3Point2: 'You will see a real-time progress bar',
      step3Point3: 'All data will be automatically extracted',
      step4Title: 'Review and save the data',
      step4Subtitle: 'Verify that the extracted data is correct before saving',
      step4Point1Title: 'Verify the data',
      step4Point1Desc: 'Price, location, bedrooms, bathrooms, etc.',
      step4Point2Title: 'Click "Save"',
      step4Point2Desc: 'If everything looks good, save the property to the database',
      step4Point3Title: 'Ready for the next one!',
      step4Point3Desc: 'Repeat the process with another property',
      understood: 'Got it! Start using',
    },
  },
};

export function getTranslation(lang: Language): Translations {
  return translations[lang];
}
