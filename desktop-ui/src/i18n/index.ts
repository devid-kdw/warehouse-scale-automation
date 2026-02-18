import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import hrCommon from './locales/hr/common.json';
import enCommon from './locales/en/common.json';
import deCommon from './locales/de/common.json';
import huCommon from './locales/hu/common.json';

const resources = {
    hr: { common: hrCommon },
    en: { common: enCommon },
    de: { common: deCommon },
    hu: { common: huCommon },
};

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources,
        defaultNS: 'common',
        fallbackLng: 'hr',
        lng: 'hr',
        interpolation: {
            escapeValue: false,
        },
        detection: {
            order: ['localStorage', 'navigator'],
            caches: ['localStorage'],
            lookupLocalStorage: 'i18nextLng',
        },
    });

export default i18n;
