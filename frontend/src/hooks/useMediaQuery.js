import { useState, useEffect } from 'react';

const breakpoints = {
    xs: 0,
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280,
    '2xl': 1536,
};

export function useMediaQuery(query) {
    const [matches, setMatches] = useState(false);

    useEffect(() => {
        const mediaQuery = window.matchMedia(query);
        setMatches(mediaQuery.matches);

        const handler = (e) => setMatches(e.matches);
        mediaQuery.addEventListener('change', handler);
        return () => mediaQuery.removeEventListener('change', handler);
    }, [query]);

    return matches;
}

export function useBreakpoint() {
    const [breakpoint, setBreakpoint] = useState('md');

    useEffect(() => {
        const checkBreakpoint = () => {
            const width = window.innerWidth;
            if (width < breakpoints.sm) setBreakpoint('xs');
            else if (width < breakpoints.md) setBreakpoint('sm');
            else if (width < breakpoints.lg) setBreakpoint('md');
            else if (width < breakpoints.xl) setBreakpoint('lg');
            else if (width < breakpoints['2xl']) setBreakpoint('xl');
            else setBreakpoint('2xl');
        };

        checkBreakpoint();
        window.addEventListener('resize', checkBreakpoint);
        return () => window.removeEventListener('resize', checkBreakpoint);
    }, []);

    return {
        breakpoint,
        isXs: breakpoint === 'xs',
        isSm: breakpoint === 'sm',
        isMd: breakpoint === 'md',
        isLg: breakpoint === 'lg',
        isXl: breakpoint === 'xl',
        is2xl: breakpoint === '2xl',
        isSmOrBelow: ['xs', 'sm'].includes(breakpoint),
        isMdOrBelow: ['xs', 'sm', 'md'].includes(breakpoint),
        isLgOrBelow: ['xs', 'sm', 'md', 'lg'].includes(breakpoint),
    };
}
