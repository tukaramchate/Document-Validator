import { useState, useCallback } from 'react';

export function usePagination(initialPage = 1, perPage = 10) {
    const [page, setPage] = useState(initialPage);
    const [total, setTotal] = useState(0);
    const [totalPages, setTotalPages] = useState(1);

    const goToPage = useCallback((newPage) => {
        if (newPage >= 1 && newPage <= totalPages) {
            setPage(newPage);
        }
    }, [totalPages]);

    const nextPage = useCallback(() => {
        goToPage(page + 1);
    }, [page, goToPage]);

    const prevPage = useCallback(() => {
        goToPage(page - 1);
    }, [page, goToPage]);

    const reset = useCallback(() => {
        setPage(1);
    }, []);

    const updateTotal = useCallback((newTotal) => {
        setTotal(newTotal);
        setTotalPages(Math.ceil(newTotal / perPage));
    }, [perPage]);

    const getPaginationRange = useCallback(() => {
        const delta = 2;
        const left = Math.max(2, page - delta);
        const right = Math.min(totalPages - 1, page + delta);
        const range = [];
        const rangeWithDots = [];

        range.push(1);
        for (let i = left; i <= right; i++) {
            range.push(i);
        }
        if (totalPages > 1) {
            range.push(totalPages);
        }

        let prev = 0;
        for (const i of range) {
            if (prev && i - prev > 1) {
                rangeWithDots.push('...');
            }
            rangeWithDots.push(i);
            prev = i;
        }

        return rangeWithDots;
    }, [page, totalPages]);

    return {
        page,
        total,
        totalPages,
        perPage,
        goToPage,
        nextPage,
        prevPage,
        reset,
        updateTotal,
        getPaginationRange,
        canGoNext: page < totalPages,
        canGoPrev: page > 1,
        hasPages: totalPages > 1
    };
}
