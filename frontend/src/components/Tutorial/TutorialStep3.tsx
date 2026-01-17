import { useLanguage } from '../../contexts/LanguageContext'
import { getTranslation } from '../../i18n/translations'

interface TutorialStep3Props {
  position?: DOMRect
  onNext: () => void
  onSkip: () => void
}

export default function TutorialStep3({ position, onNext, onSkip }: TutorialStep3Props) {
  const { language } = useLanguage()
  const t = getTranslation(language)

  if (!position) return null

  return (
    <>
      {/* Animated arrow */}
      <div
        className="absolute pointer-events-none z-50"
        style={{
          top: `${position.top + window.scrollY - 120}px`,
          left: `${position.left + position.width / 2}px`,
          transform: 'translateX(-50%)',
        }}
      >
        <div className="flex flex-col items-center">
          <svg className="w-24 h-24 text-yellow-500 animate-bounce" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z" transform="rotate(90 12 12)" />
          </svg>
          <div className="bg-yellow-500 text-white px-6 py-3 rounded-full font-bold text-lg shadow-2xl whitespace-nowrap mt-2">
            {t.tutorial.clickHere}
          </div>
        </div>
      </div>

      {/* Glowing highlight box */}
      <div
        className="absolute pointer-events-none border-4 border-yellow-400 rounded-lg shadow-2xl"
        style={{
          top: `${position.top + window.scrollY}px`,
          left: `${position.left}px`,
          width: `${position.width}px`,
          height: `${position.height}px`,
          zIndex: 55,
          animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite, glowYellow 2s ease-in-out infinite',
          boxShadow: '0 0 0 4px rgba(234, 179, 8, 0.3), 0 0 30px rgba(234, 179, 8, 0.5), inset 0 0 20px rgba(234, 179, 8, 0.2)'
        }}
      />

      {/* Instruction card */}
      <div
        className="absolute pointer-events-auto bg-white rounded-lg shadow-2xl"
        style={{
          bottom: '5%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '90%',
          maxWidth: '500px',
          zIndex: 60
        }}
      >
        <div className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white p-4 rounded-t-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-white text-yellow-600 rounded-full w-10 h-10 flex items-center justify-center font-bold text-xl">
                3
              </div>
              <div>
                <h3 className="text-xl font-bold">{t.tutorial.step3Title}</h3>
                <p className="text-xs text-yellow-100">{t.tutorial.step3Subtitle}</p>
              </div>
            </div>
            <button onClick={onSkip} className="text-white/80 hover:text-white">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <div className="p-4">
          <div className="space-y-2 mb-4">
            <div className="flex items-center gap-2 text-sm">
              <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-gray-700">{t.tutorial.step3Point1}</p>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <p className="text-gray-700">{t.tutorial.step3Point2}</p>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
              <p className="text-gray-700">{t.tutorial.step3Point3}</p>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={onNext}
              className="flex-1 bg-yellow-600 text-white py-3 px-6 rounded-lg font-bold hover:bg-yellow-700 transition-all flex items-center justify-center gap-2"
            >
              {t.tutorial.next}
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </button>
            <button
              onClick={onSkip}
              className="px-6 py-3 text-gray-600 hover:text-gray-800 font-medium"
            >
              {t.tutorial.skip}
            </button>
          </div>
        </div>
      </div>

      {/* Yellow glow animation */}
      <style>{`
        @keyframes glowYellow {
          0%, 100% {
            box-shadow: 0 0 0 4px rgba(234, 179, 8, 0.3), 0 0 30px rgba(234, 179, 8, 0.5), inset 0 0 20px rgba(234, 179, 8, 0.2);
          }
          50% {
            box-shadow: 0 0 0 8px rgba(234, 179, 8, 0.4), 0 0 50px rgba(234, 179, 8, 0.7), inset 0 0 30px rgba(234, 179, 8, 0.3);
          }
        }
      `}</style>
    </>
  )
}
