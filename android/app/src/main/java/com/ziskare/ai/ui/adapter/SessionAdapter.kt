package com.ziskare.ai.ui.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.ziskare.ai.R
import com.ziskare.ai.db.entity.Session
import java.text.SimpleDateFormat
import java.util.*

class SessionAdapter(
    private val onClick: (Session) -> Unit,
    private val onLongClick: (Session) -> Boolean,
    private val onDelete: (Session) -> Unit
) : ListAdapter<Session, SessionAdapter.VH>(Diff()) {

    override fun onCreateViewHolder(parent: ViewGroup, type: Int) =
        VH(LayoutInflater.from(parent.context).inflate(R.layout.item_session, parent, false))

    override fun onBindViewHolder(holder: VH, pos: Int) = holder.bind(getItem(pos))

    inner class VH(v: View) : RecyclerView.ViewHolder(v) {
        private val tvTitle: TextView = v.findViewById(R.id.tvSessionTitle)
        private val tvTime: TextView = v.findViewById(R.id.tvSessionTime)
        private val btnDel: ImageButton = v.findViewById(R.id.btnDeleteSession)

        fun bind(s: Session) {
            tvTitle.text = s.title
            tvTime.text = SimpleDateFormat("MMM d", Locale.getDefault()).format(Date(s.lastMessageAt))
            itemView.setOnClickListener { onClick(s) }
            itemView.setOnLongClickListener { onLongClick(s) }
            btnDel.setOnClickListener { onDelete(s) }
        }
    }

    class Diff : DiffUtil.ItemCallback<Session>() {
        override fun areItemsTheSame(a: Session, b: Session) = a.id == b.id
        override fun areContentsTheSame(a: Session, b: Session) = a == b
    }
}
