export const Home = () => {
    return (
        <div className="flex-1 flex flex-col">
            <section className="relative overflow-hidden flex-1 flex items-center justify-center py-12 bg-gradient-to-b from-background via-background/90 to-muted/30">
                <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-primary/10 rounded-full blur-3xl pointer-events-none -z-10" />
                <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-foreground max-w-4xl mx-auto leading-tight">
                        Fix Your City <br className="hidden sm:inline" />
                        <span className="text-primary">Without Compromising Anonymity</span>
                    </h1>
                    <p className="mt-6 text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                        Report civic hazards instantly without creating an account or revealing your
                        identity. Track resolutions in real-time with zero-knowledge token codes.
                    </p>
                </div>
            </section>
        </div>
    );
};
