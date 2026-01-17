import React from 'react'
import { useLanguage } from '../../contexts/LanguageContext'
import { getTranslation } from '../../i18n/translations'

interface TutorialStep4Props {
  onSkip: () => void
}

export default function TutorialStep4({ onSkip }: TutorialStep4Props) {
  const { language } = useLanguage()
  const t = getTranslation(language)
  return (
    <div
      className="absolute pointer-events-auto bg-white rounded-lg shadow-2xl"
      style={{
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '90%',
        maxWidth: '500px',
        zIndex: 60
      }}
    >
      <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 rounded-t-lg">
        <div className="flex items-center gap-3 mb-2">
          <div className="bg-white text-purple-600 rounded-full w-10 h-10 flex items-center justify-center font-bold text-xl">
            4
          </div>
          <h3 className="text-2xl font-bold">{t.tutorial.step4Title}</h3>
        </div>
        <p className="text-purple-100">{t.tutorial.step4Subtitle}</p>
      </div>
      <div className="p-6">
        <div className="space-y-4 mb-6">
          <div className="flex items-start gap-3 bg-purple-50 rounded-lg p-4 border-l-4 border-purple-400">
            <svg className="w-6 h-6 text-purple-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <div>
              <p className="font-bold text-gray-800">{t.tutorial.step4Point1Title}</p>
              <p className="text-sm text-gray-600">{t.tutorial.step4Point1Desc}</p>
            </div>
          </div>
          <div className="flex items-start gap-3 bg-purple-50 rounded-lg p-4 border-l-4 border-purple-400">
            <svg className="w-6 h-6 text-purple-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
            </svg>
            <div>
              <p className="font-bold text-gray-800">{t.tutorial.step4Point2Title}</p>
              <p className="text-sm text-gray-600">{t.tutorial.step4Point2Desc}</p>
            </div>
          </div>
          <div className="flex items-start gap-3 bg-purple-50 rounded-lg p-4 border-l-4 border-purple-400">
            <svg className="w-6 h-6 text-purple-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <div>
              <p className="font-bold text-gray-800">{t.tutorial.step4Point3Title}</p>
              <p className="text-sm text-gray-600">{t.tutorial.step4Point3Desc}</p>
            </div>
          </div>
        </div>
        <button
          onClick={onSkip}
          className="w-full bg-gradient-to-r from-purple-600 to-purple-700 text-white py-4 px-6 rounded-lg font-bold hover:from-purple-700 hover:to-purple-800 transition-all flex items-center justify-center gap-2 text-lg"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {t.tutorial.understood}
        </button>
      </div>
    </div>
  )
}
