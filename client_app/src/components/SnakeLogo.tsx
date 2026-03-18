import snakeImg from "../assets/snake.png";

export function SnakeLogo({ size = 32 }: { size?: number }) {
  return (
    <img
      src={snakeImg}
      width={size}
      height={size}
      style={{ objectFit: "contain" }}
    />
  );
}