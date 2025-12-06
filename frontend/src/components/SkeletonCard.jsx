import { motion } from 'framer-motion';

export function SkeletonCard({ view }) {
    if (view === 'list') {
        return (
            <div className="flex items-center gap-4 py-2 opacity-50">
                <div className="w-12 h-12 bg-white/10 rounded-md animate-pulse shrink-0" />
                <div className="flex-1 min-w-0 space-y-2">
                    <div className="h-4 bg-white/10 rounded w-1/3 animate-pulse" />
                    <div className="h-3 bg-white/10 rounded w-1/4 animate-pulse" />
                </div>
            </div>
        )
    }

    return (
        <div className="p-4 bg-white/5 rounded-xl border border-white/5 flex flex-col gap-3 min-h-[180px] animate-pulse">
            <div className="w-full aspect-square bg-white/10 rounded-lg shrink-0" />
            <div className="space-y-2 mt-auto">
                <div className="h-4 bg-white/10 rounded w-3/4" />
                <div className="h-3 bg-white/10 rounded w-1/2" />
            </div>
        </div>
    );
}
