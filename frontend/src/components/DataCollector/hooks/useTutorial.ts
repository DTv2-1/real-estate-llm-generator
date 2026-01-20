/**
 * useTutorial Hook
 * 
 * Manages interactive tutorial state and navigation
 */

import { useState } from 'react'

export const useTutorial = () => {
  const [tutorialStep, setTutorialStep] = useState<number | null>(null)
  const [showTutorialButton, setShowTutorialButton] = useState(true)
  const [highlightPositions, setHighlightPositions] = useState<{
    urlInput?: DOMRect
    processButton?: DOMRect
  }>({})

  /**
   * Calculate DOM positions for highlighted elements
   */
  const calculateHighlightPositions = () => {
    const urlInput = document.getElementById('propertyUrlInput')
    const processButton = document.getElementById('processPropertyButton')
    
    const positions: any = {}
    
    if (urlInput) {
      positions.urlInput = urlInput.getBoundingClientRect()
    }
    if (processButton) {
      positions.processButton = processButton.getBoundingClientRect()
    }
    
    setHighlightPositions(positions)
  }

  /**
   * Start the tutorial
   */
  const startTutorial = () => {
    setTutorialStep(1)
    setShowTutorialButton(false)
    // Calculate positions after state updates
    setTimeout(calculateHighlightPositions, 100)
  }

  /**
   * Advance to next tutorial step
   */
  const nextTutorialStep = () => {
    if (tutorialStep !== null && tutorialStep < 3) {
      setTutorialStep(tutorialStep + 1)
      setTimeout(calculateHighlightPositions, 100)
    } else {
      endTutorial()
    }
  }

  /**
   * Skip/end the tutorial
   */
  const skipTutorial = () => {
    endTutorial()
  }

  /**
   * End tutorial and reset state
   */
  const endTutorial = () => {
    setTutorialStep(null)
    setShowTutorialButton(true)
  }

  /**
   * Restart tutorial from beginning
   */
  const restartTutorial = () => {
    startTutorial()
  }

  return {
    tutorialStep,
    showTutorialButton,
    highlightPositions,
    startTutorial,
    nextTutorialStep,
    skipTutorial,
    calculateHighlightPositions,
    restartTutorial
  }
}
