export default function Footer() {
    return (
        <footer className="border-t border-surface-800/50 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                    <div className="flex items-center gap-2">
                        <div className="w-6 h-6 bg-gradient-to-br from-brand-500 to-brand-700 rounded-md flex items-center justify-center">
                            <span className="text-white font-bold text-xs">DV</span>
                        </div>
                        <span className="text-sm text-surface-400">
                            DocValidator — AI-Powered Document Verification
                        </span>
                    </div>
                    <p className="text-xs text-surface-500">
                        © {new Date().getFullYear()} DocValidator. All rights reserved.
                    </p>
                </div>
            </div>
        </footer>
    );
}
