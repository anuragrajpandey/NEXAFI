import NEXAFILogo from '../assets/NEXAFI.png';

interface LogoProps {
  className?: string;
  width?: number | string;
  height?: number | string;
}

export function Logo({ className, width, height }: LogoProps) {
  return (
    <img
      className={className}
      src={NEXAFILogo}
      width={width}
      height={height}
      alt="NEXAFI TV"
      draggable={false}
      style={{ objectFit: 'contain' }}
    />
  );
}
