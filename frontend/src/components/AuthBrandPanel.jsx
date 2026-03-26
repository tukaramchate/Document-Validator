import { ShieldCheck } from 'lucide-react';

/**
 * Shared left-side brand panel used on Login and Register pages.
 * Eliminates the 50-line duplication between the two files.
 */
export default function AuthBrandPanel() {
    return (
        <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-brand-500 via-brand-600 to-brand-700 text-white relative overflow-hidden">
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-10">
                <div className="absolute top-20 right-20 w-96 h-96 bg-white rounded-full blur-3xl" />
                <div className="absolute bottom-20 left-20 w-80 h-80 bg-white rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 p-12 flex flex-col justify-center w-full">
                <div className="mb-8">
                    <div className="inline-flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                            <ShieldCheck className="text-white" size={24} />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold">VeriAcd</h1>
                            <p className="text-sm text-white/80">AI-Powered Document Verification</p>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <h2 className="text-4xl font-bold leading-tight">Secure Academic Verification</h2>

                    <p className="text-lg text-white/90">
                        Join thousands of institutions and verifiers using the most trusted certificate validation platform.
                    </p>

                    <div className="space-y-4">
                        {['Authorized Platform', 'Professional-Grade Security', 'Upto 99.7% Accuracy Rate'].map((item) => (
                            <div key={item} className="flex items-center gap-3">
                                <div className="w-5 h-5 rounded-full bg-white/30 flex items-center justify-center">
                                    <div className="w-2 h-2 bg-white rounded-full" />
                                </div>
                                <span>{item}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
