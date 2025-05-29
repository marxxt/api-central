export const ComponentSizes = {
  sm: "sm",
  DEFAULT: "DEFAULT",
  lg: "lg",
  xl: "xl",
} as const; // Use "as const" for literal types

export type ComponentSize = keyof typeof ComponentSizes;
