import { useState, useCallback } from 'react';

export function useForm(initialValues, onSubmit) {
    const [values, setValues] = useState(initialValues);
    const [errors, setErrors] = useState({});
    const [touched, setTouched] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleChange = useCallback((e) => {
        const { name, value, type, checked } = e.target;
        setValues(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
        // Clear error for this field
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: undefined
            }));
        }
    }, [errors]);

    const handleBlur = useCallback((e) => {
        const { name } = e.target;
        setTouched(prev => ({
            ...prev,
            [name]: true
        }));
    }, []);

    const handleSubmit = useCallback(async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        try {
            await onSubmit(values);
        } catch (error) {
            if (error.validationErrors) {
                setErrors(error.validationErrors);
            }
        } finally {
            setIsSubmitting(false);
        }
    }, [values, onSubmit]);

    const resetForm = useCallback(() => {
        setValues(initialValues);
        setErrors({});
        setTouched({});
    }, [initialValues]);

    const setFieldValue = useCallback((name, value) => {
        setValues(prev => ({
            ...prev,
            [name]: value
        }));
    }, []);

    const setFieldError = useCallback((name, error) => {
        setErrors(prev => ({
            ...prev,
            [name]: error
        }));
    }, []);

    return {
        values,
        errors,
        touched,
        isSubmitting,
        handleChange,
        handleBlur,
        handleSubmit,
        resetForm,
        setFieldValue,
        setFieldError,
        setValues,
        setErrors
    };
}

export function useFieldArray(initialValues = []) {
    const [fields, setFields] = useState(initialValues);

    const push = useCallback((value) => {
        setFields(prev => [...prev, value]);
    }, []);

    const remove = useCallback((index) => {
        setFields(prev => prev.filter((_, i) => i !== index));
    }, []);

    const insert = useCallback((index, value) => {
        setFields(prev => {
            const newFields = [...prev];
            newFields.splice(index, 0, value);
            return newFields;
        });
    }, []);

    const move = useCallback((from, to) => {
        setFields(prev => {
            const newFields = [...prev];
            const item = newFields.splice(from, 1)[0];
            newFields.splice(to, 0, item);
            return newFields;
        });
    }, []);

    const reset = useCallback((values = []) => {
        setFields(values);
    }, []);

    return {
        fields,
        push,
        remove,
        insert,
        move,
        reset,
        set: setFields
    };
}
