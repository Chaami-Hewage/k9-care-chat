import { ContactShadows, useTexture } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import { useEffect, useRef } from "react";
import * as THREE from "three";

import mascotAsset from "@/assets/know-your-dog-mascot.png.asset.json";

type PointerTarget = {
  x: number;
  y: number;
  activeUntil: number;
};

type SpringChannel = {
  value: number;
  velocity: number;
};

function spring(
  channel: SpringChannel,
  target: number,
  delta: number,
  stiffness = 72,
  damping = 13,
) {
  const force = (target - channel.value) * stiffness;
  channel.velocity += force * delta;
  channel.velocity *= Math.exp(-damping * delta);
  channel.value += channel.velocity * delta;
}

function DogCutout({
  pointer,
  action,
}: {
  pointer: React.RefObject<PointerTarget>;
  action: number;
}) {
  const group = useRef<THREE.Group>(null);
  const texture = useTexture(mascotAsset.url);
  const lastAction = useRef(action);
  const rollTarget = useRef(0);
  const jumpStartedAt = useRef(-10);
  const xRotation = useRef<SpringChannel>({ value: 0, velocity: 0 });
  const yRotation = useRef<SpringChannel>({ value: 0, velocity: 0 });
  const zRotation = useRef<SpringChannel>({ value: 0, velocity: 0 });
  const yPosition = useRef<SpringChannel>({ value: 0, velocity: 0 });
  const scale = useRef<SpringChannel>({ value: 1, velocity: 0 });

  useEffect(() => {
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = 8;
    texture.needsUpdate = true;
  }, [texture]);

  useEffect(() => {
    if (action === lastAction.current) return;
    lastAction.current = action;
    rollTarget.current += Math.PI * 2;
    jumpStartedAt.current = performance.now() / 1000;
  }, [action]);

  useFrame(({ clock }, rawDelta) => {
    const model = group.current;
    const target = pointer.current;
    if (!model || !target) return;

    const delta = Math.min(rawDelta, 1 / 30);
    const elapsed = clock.getElapsedTime();
    const now = performance.now();
    const tracking = now < target.activeUntil;
    const idle = tracking ? 0 : 1;
    const idleFloat = Math.sin(elapsed * 0.9) * 0.11 * idle;
    const idleScale = 1 + Math.sin(elapsed * 0.9 + 0.6) * 0.018 * idle;
    const jumpAge = performance.now() / 1000 - jumpStartedAt.current;
    const jumpProgress = THREE.MathUtils.clamp(jumpAge / 0.95, 0, 1);
    const jump = jumpAge < 0.95 ? Math.sin(jumpProgress * Math.PI) * 0.62 : 0;
    const squash = jumpAge < 0.95 ? Math.sin(jumpProgress * Math.PI * 2) * 0.035 : 0;

    spring(xRotation.current, tracking ? target.y * 0.34 : Math.sin(elapsed * 0.45) * 0.025, delta);
    spring(yRotation.current, tracking ? target.x * 0.48 : Math.sin(elapsed * 0.35) * 0.045, delta);
    spring(zRotation.current, rollTarget.current, delta, 92, 14);
    spring(yPosition.current, idleFloat + jump, delta, 84, 14);
    spring(scale.current, idleScale - squash, delta, 82, 14);

    model.rotation.x = xRotation.current.value;
    model.rotation.y = yRotation.current.value;
    model.rotation.z = zRotation.current.value;
    model.position.y = yPosition.current.value;
    model.scale.setScalar(scale.current.value);
  });

  return (
    <group ref={group} position={[0, 0.08, 0]}>
      {[-0.12, -0.08, -0.04].map((depth, index) => (
        <mesh key={depth} position={[0, -0.015 * index, depth]} scale={1 - index * 0.018}>
          <planeGeometry args={[3.25, 3.25]} />
          <meshBasicMaterial
            map={texture}
            transparent
            alphaTest={0.03}
            color={index === 0 ? "#7d89b5" : "#a9b1cf"}
            opacity={0.2}
            depthWrite={false}
            toneMapped={false}
          />
        </mesh>
      ))}
      <mesh position={[0, 0, 0.01]}>
        <planeGeometry args={[3.25, 3.25]} />
        <meshBasicMaterial
          map={texture}
          transparent
          alphaTest={0.03}
          depthWrite={false}
          toneMapped={false}
        />
      </mesh>
    </group>
  );
}

export default function DogHero3D({
  pointer,
  action,
}: {
  pointer: React.RefObject<PointerTarget>;
  action: number;
}) {
  return (
    <Canvas
      dpr={[1, 2]}
      camera={{ position: [0, 0.05, 5.4], fov: 36 }}
      gl={{ alpha: true, antialias: true }}
      style={{ background: "transparent" }}
    >
      <ambientLight intensity={1.5} />
      <directionalLight position={[3, 4, 5]} intensity={1.2} />
      <DogCutout pointer={pointer} action={action} />
      <ContactShadows
        position={[0, -1.52, -0.25]}
        opacity={0.28}
        scale={3.2}
        blur={2.8}
        far={3}
        color="#313652"
      />
    </Canvas>
  );
}