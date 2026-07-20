/**
 * The one button (Design System §1; Doc 06 §8): subtractive premium — no
 * gradient-of-hype, no badge noise. Three variants carry every action in
 * the product: primary (the accent, one per view at most), secondary
 * (hairline), and quiet (text-weight acts). Chips remain their own shape.
 */
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "transition-settle inline-flex items-center justify-center gap-2 rounded-control text-sm font-medium disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-accent text-accent-ink hover:opacity-90",
        outline: "border border-hairline bg-transparent text-ink hover:bg-paper",
        quiet: "text-ink-faint hover:text-ink",
      },
      size: {
        default: "px-3 py-1.5",
        sm: "px-2.5 py-1 text-xs",
        lg: "px-4 py-2",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
