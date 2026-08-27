import type { ReactNode } from "react";

export function SectionRule({
  title,
  note,
  children,
}: {
  title: string;
  note?: string;
  children?: ReactNode;
}) {
  return (
    <div className="section-rule">
      <div>
        <h2>{title}</h2>
        {note ? <p>{note}</p> : null}
      </div>
      {children ? <div className="section-rule-action">{children}</div> : null}
    </div>
  );
}
