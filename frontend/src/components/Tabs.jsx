import { useState } from 'react';
import { useTheme } from '../context/ThemeContext';

export function Tabs({ tabs, defaultTab = 0, onChange }) {
    const [activeTab, setActiveTab] = useState(defaultTab);
    const { theme } = useTheme();
    const isDark = theme === 'dark';

    const handleTabChange = (index) => {
        setActiveTab(index);
        onChange?.(index, tabs[index]);
    };

    return (
        <div>
            {/* Tab List */}
            <div className={`flex gap-2 border-b ${isDark ? 'border-surface-800/50' : 'border-surface-200'} mb-6`}>
                {tabs.map((tab, index) => (
                    <button
                        key={index}
                        onClick={() => handleTabChange(index)}
                        className={`pb-3 px-4 font-semibold transition-all ${
                            activeTab === index
                                ? 'text-brand-500 border-b-2 border-brand-500'
                                : isDark
                                ? 'text-surface-400 hover:text-surface-200'
                                : 'text-surface-600 hover:text-surface-900'
                        }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div>
                {tabs[activeTab]?.content}
            </div>
        </div>
    );
}

export function Accordion({ items, allowMultiple = false }) {
    const [expanded, setExpanded] = useState(allowMultiple ? [] : null);
    const { theme } = useTheme();
    const isDark = theme === 'dark';

    const toggleItem = (index) => {
        if (allowMultiple) {
            setExpanded(exp => 
                exp.includes(index) 
                    ? exp.filter(i => i !== index)
                    : [...exp, index]
            );
        } else {
            setExpanded(exp => exp === index ? null : index);
        }
    };

    return (
        <div className="space-y-3">
            {items.map((item, index) => (
                <div key={index} className={`border rounded-lg overflow-hidden ${isDark ? 'border-surface-800/50' : 'border-surface-200'}`}>
                    <button
                        onClick={() => toggleItem(index)}
                        className={`w-full flex items-center justify-between p-4 transition-colors text-left font-semibold ${
                            isDark
                                ? 'hover:bg-surface-800/30 text-surface-100'
                                : 'hover:bg-surface-50 text-surface-900'
                        }`}
                    >
                        <span>{item.title}</span>
                        <span className={`${isDark ? 'text-surface-500' : 'text-surface-400'} transition-transform ${
                            allowMultiple 
                                ? (expanded.includes(index) ? 'rotate-180' : '')
                                : (expanded === index ? 'rotate-180' : '')
                        }`}>
                            ▽
                        </span>
                    </button>
                    {((allowMultiple && expanded.includes(index)) || (!allowMultiple && expanded === index)) && (
                        <div className={`px-4 py-3 border-t ${isDark ? 'bg-surface-900/50 border-surface-800/50 text-surface-300' : 'bg-surface-50 border-surface-200 text-surface-700'}`}>
                            {item.content}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}
