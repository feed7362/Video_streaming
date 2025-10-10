import {useState} from "react";
import {Button} from "@/components/ui/button";
import {CheckCircle2, XCircle, Info, ArrowRight, Download} from "lucide-react";
import {cn} from "@/lib/utils";

type Feature = {
    text: string;
    included: boolean;
};

type Plan = {
    name: string;
    description: string;
    priceMonthly: number;
    priceYearly: number;
    billedYearlyText: string;
    discount?: string;
    isPopular?: boolean;
    buttonText: string;
    buttonColorClass: string;
    features: Feature[];
    additionalFeatures: Feature[];
};

const plans: Plan[] = [
    {
        name: "Free",
        description: "Try us out for a quick project or two",
        priceMonthly: 0,
        priceYearly: 0,
        billedYearlyText: "Upgrade any time",
        buttonText: "Get started",
        buttonColorClass: "bg-black hover:bg-gray-800 text-white",
        features: [
            {text: "1 active project", included: true},
            {text: "3 MB upload limit", included: true},
            {text: "5,000 visitors /mo", included: true}
        ],
        additionalFeatures: [
            {text: "Remove Tiny Host banner", included: false},
            {text: "QR codes", included: false},
            {text: "Built-in Analytics", included: false}
        ]
    },
    {
        name: "Tiny",
        description: "Perfect for a single, professional link",
        priceMonthly: 5,
        priceYearly: 60,
        billedYearlyText: "Billed at $60 /yr",
        discount: "44% off",
        buttonText: "Get started",
        buttonColorClass: "bg-[#007bff] hover:bg-[#0069d9] text-white",
        features: [
            {text: "1 active project", included: true},
            {text: "25 MB upload limit", included: true},
            {text: "10,000 visitors /mo", included: true}
        ],
        additionalFeatures: [
            {text: "Remove Tiny Host banner", included: true},
            {text: "QR codes", included: true},
            {text: "Built-in Analytics", included: true}
        ]
    },
    {
        name: "Solo",
        description: "Great for small projects",
        priceMonthly: 13,
        priceYearly: 156,
        billedYearlyText: "Billed at $156 /yr",
        discount: "27% off",
        isPopular: true,
        buttonText: "Get started",
        buttonColorClass: "bg-[#8a2be2] hover:bg-[#7a24cc] text-white",
        features: [
            {text: "5 active projects", included: true},
            {text: "75 MB upload limit", included: true},
            {text: "100,000 visitors /mo", included: true}
        ],
        additionalFeatures: [
            {text: "Everything in Tiny Plan", included: true},
            {text: "Custom domains", included: true},
            {text: "Edit mode", included: true},
            {text: "Password protection", included: true}
        ]
    },
    {
        name: "Pro",
        description: "For freelancers, agencies & companies",
        priceMonthly: 31,
        priceYearly: 372,
        billedYearlyText: "Billed at $372 /yr",
        discount: "18% off",
        buttonText: "Get started",
        buttonColorClass: "bg-[#ffc107] hover:bg-[#e0a800] text-black",
        features: [
            {text: "Unlimited active projects", included: true},
            {text: "10 GB upload limit", included: true},
            {text: "500,000 visitors /mo", included: true}
        ],
        additionalFeatures: [
            {text: "Everything in Solo Plan", included: true},
            {text: "Capture emails", included: true},
            {text: "Add more team members", included: true}
        ]
    }
];

export default function PricingTable() {
    const [isYearly, setIsYearly] = useState(true);

    return (
        <div className="min-h-screen px-4 py-12 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-7xl">
                <header className="mb-12 space-y-4 text-center">
                    <h1 className="text-4xl font-bold md:text-5xl">Pricing</h1>
                    <p className="text-muted-foreground text-lg text-balance">
                        Upgrade to link your custom domain, track your visits, edit your content & much more.
                    </p>
                </header>

                <div className="mb-12 text-center">
                    <div className="bg-muted inline-flex items-center rounded-full p-1">
                        <button
                            className={cn(
                                "rounded-full px-6 py-2 text-sm font-medium transition-colors",
                                !isYearly ? "bg-gray-200" : "text-muted-foreground"
                            )}
                            onClick={() => setIsYearly(false)}>
                            Monthly
                        </button>
                        <button
                            className={cn(
                                "rounded-full px-6 py-2 text-sm font-medium transition-colors",
                                isYearly ? "bg-black text-white" : "text-muted-foreground"
                            )}
                            onClick={() => setIsYearly(true)}>
                            Yearly
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4 lg:gap-8">
                    {plans.map((plan) => (
                        <div
                            key={plan.name}
                            className={cn(
                                "bg-muted relative flex flex-col rounded-xl border p-6",
                                plan.isPopular && "border-2 border-[#8a2be2] shadow-xl"
                            )}>
                            {plan.isPopular && (
                                <div
                                    className="absolute -top-4 left-1/2 -translate-x-1/2 rounded-full bg-[#8a2be2] px-3 py-1 text-xs font-semibold text-white">
                                    Most Popular
                                </div>
                            )}
                            <h2 className="mb-2 text-2xl font-semibold">{plan.name}</h2>
                            <p className="text-muted-foreground mb-4 text-sm">{plan.description}</p>

                            {plan.discount && (
                                <div
                                    className={cn(
                                        "absolute top-6 right-6 rounded-full px-2 py-1 text-xs font-semibold",
                                        plan.name === "Tiny" && "bg-background text-[#007bff]",
                                        plan.name === "Solo" && "bg-background text-[#8a2be2]",
                                        plan.name === "Pro" && "bg-background text-[#ffc107]"
                                    )}>
                                    {plan.discount}
                                </div>
                            )}

                            <div className="mb-6 flex items-baseline">
                <span className="text-5xl font-bold">
                  ${plan.name === "Free" ? 0 : isYearly ? plan.priceYearly : plan.priceMonthly}
                </span>
                                <span className="text-muted-foreground text-xl">
                  {plan.name === "Free" ? "/mo" : isYearly ? "/yr" : "/mo"}
                </span>
                            </div>
                            <p className="text-muted-foreground mb-6 text-sm">
                                {plan.name === "Free"
                                    ? plan.billedYearlyText
                                    : isYearly
                                        ? plan.billedYearlyText
                                        : "Billed monthly"}
                            </p>

                            <Button className={cn("font-medium", plan.buttonColorClass)}>
                                {plan.buttonText} <ArrowRight/>
                            </Button>

                            <div className="text-muted-foreground mt-4 mb-6 flex items-center justify-center text-xs">
                                <Info className="mr-1 size-3"/>
                                <span>7-day money-back guarantee</span>
                            </div>

                            <div className="flex-grow">
                                <ul className="text-muted-foreground space-y-3 text-left">
                                    {plan.features.map((feature, index) => (
                                        <li key={index} className="flex items-center text-sm">
                                            {feature.included ? (
                                                <CheckCircle2 className="mr-2 h-4 w-4 flex-shrink-0 text-green-500"/>
                                            ) : (
                                                <XCircle className="mr-2 h-4 w-4 flex-shrink-0 text-red-500"/>
                                            )}
                                            {feature.text}
                                        </li>
                                    ))}
                                </ul>

                                {plan.additionalFeatures.length > 0 && (
                                    <>
                                        <h3 className="mt-6 mb-3 text-sm font-semibold">Additional Features:</h3>
                                        <ul className="text-muted-foreground space-y-3 text-left">
                                            {plan.additionalFeatures.map((feature, index) => (
                                                <li key={index} className="flex items-center text-sm">
                                                    {feature.included ? (
                                                        <CheckCircle2
                                                            className="mr-2 h-4 w-4 flex-shrink-0 text-green-500"/>
                                                    ) : (
                                                        <XCircle className="mr-2 h-4 w-4 flex-shrink-0 text-red-500"/>
                                                    )}
                                                    {feature.text}
                                                </li>
                                            ))}
                                        </ul>
                                    </>
                                )}
                            </div>

                            <Button variant="ghost" className="text-muted-foreground hover: mt-8 w-full">
                                Compare plans <Download className="ml-2 h-4 w-4"/>
                            </Button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
