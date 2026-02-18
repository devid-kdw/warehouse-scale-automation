import { Menu, Button } from '@mantine/core';
import { IconLanguage } from '@tabler/icons-react';
import { useTranslation } from 'react-i18next';

const LANGUAGES = [
    { code: 'hr', name: 'Hrvatski' },
    { code: 'en', name: 'English' },
    { code: 'de', name: 'Deutsch' },
    { code: 'hu', name: 'Magyar' },
];

export function LanguageSwitcher() {
    const { i18n } = useTranslation('common');

    const handleLanguageChange = (languageCode: string) => {
        i18n.changeLanguage(languageCode);
    };

    const currentLanguage = LANGUAGES.find(lang => lang.code === i18n.language) || LANGUAGES[0];

    return (
        <Menu shadow="md" width={150}>
            <Menu.Target>
                <Button
                    variant="subtle"
                    color="gray"
                    leftSection={<IconLanguage size={16} />}
                >
                    {currentLanguage.name}
                </Button>
            </Menu.Target>
            <Menu.Dropdown>
                {LANGUAGES.map((language) => (
                    <Menu.Item
                        key={language.code}
                        onClick={() => handleLanguageChange(language.code)}
                        style={{
                            fontWeight: i18n.language === language.code ? 700 : 400,
                        }}
                    >
                        {language.name}
                    </Menu.Item>
                ))}
            </Menu.Dropdown>
        </Menu>
    );
}
